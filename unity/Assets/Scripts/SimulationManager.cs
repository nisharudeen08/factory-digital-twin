using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NativeWebSocket;

// ─────────────────────────────────────────────────────────────────────────────
// WebSocket message models
// ─────────────────────────────────────────────────────────────────────────────

[System.Serializable]
public class StationConfig
{
    public int    id;
    public string name;
    public string name_ta;
    public string icon;
    public int    num_machines;
    public float  position_x;
    public float  position_z;
    public float  cycle_time_sec;
    public float  mtbf_hours;
    public float  mttr_hours;
}

[System.Serializable]
public class FactoryConfig
{
    public string          factory_name;
    public float           shift_hours;
    public int             num_operators;
    public string          language;
    public StationConfig[] stations;
}

[Serializable]
public class WSStateUpdate
{
    public string type;
    public float  t;
    public int[]  bottleneck_ids;
    public WSStationMetric[] stations;
}

[Serializable]
public class WSStationMetric
{
    public int    station_id;
    public float  utilization;
    public float  queue_length;
    public string status;
}

/// <summary>
/// Python broadcasts: {"type":"config_update","config":{...full factory config...}}
/// We capture the raw message string and re-serialise the config sub-object.
/// </summary>
[Serializable]
public class WSConfigUpdateWrapper
{
    public string type;
    // "config" is a nested JSON object — JsonUtility can't deserialise arbitrary objects,
    // so we use the raw message and extract the inner JSON manually.
}

// ─────────────────────────────────────────────────────────────────────────────
// SimulationManager
// ─────────────────────────────────────────────────────────────────────────────

public class SimulationManager : MonoBehaviour
{
    public static SimulationManager Instance { get; private set; }
    public static bool SuppressAutoConnectForTests { get; set; }
    [Header("Python Server Connection")]
    [SerializeField]
    private string pythonServerIP = "factory-twin-server.onrender.com"; // Default to cloud IP

    [SerializeField]
    private int pythonServerPort = 8765;

    public string WebSocketUrl
    {
        get
        {
            // Cloud deployment handling (Render, Railway, Fly.io)
            if (pythonServerIP.Contains(".onrender.com") ||
                pythonServerIP.Contains(".railway.app") ||
                pythonServerIP.Contains(".fly.dev"))
            {
                return "wss://" + pythonServerIP;
            }
            // Local network handling
            return $"ws://{pythonServerIP}:{pythonServerPort}";
        }
    }

    [Tooltip("Uncheck to disable WebSocket connection for standalone testing")]
    public bool   autoConnect  = true;
    public float  reconnectDelay = 30f; // seconds — 30s reduces log spam when Python server is offline

    public MachineSpawner spawner;

    private WebSocket websocket;
    private bool isReconnecting = false;

    // Station → all machine visuals at that station
    private readonly Dictionary<int, List<MachineVisual>> stationMachines =
        new Dictionary<int, List<MachineVisual>>();

    // ─────────────────────────────────────────────────────────────────────────
    // Android config reception state
    // ─────────────────────────────────────────────────────────────────────────

    // Tracks if Android has sent config; takes priority over Python updates
    private bool androidConfigReceived = false;

    // Stores the JSON received from Android if Unity isn't ready yet
    private string _pendingAndroidJson = null;

    // Set to true once Update() has run at least once (guarantees main thread
    // is fully active and MonoBehaviours are initialized)
    private bool _unityIsReady = false;

    private Coroutine activeSpawnCoroutine;

    // ─────────────────────────────────────────────────────────────────────────
    // Unity lifecycle
    // ─────────────────────────────────────────────────────────────────────────

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        // In the Editor, reset this to false so WebSocket broadcasts work immediately
        androidConfigReceived = false;
    }

    async void Start()
    {
        Debug.Log("[SM] Start() called — Unity main thread is ready.");
        _unityIsReady = true;

        // If Android already delivered config before Start(), process it now
        if (!string.IsNullOrEmpty(_pendingAndroidJson))
        {
            Debug.Log("[SM] Flushing pending Android config received before Start().");
            string json = _pendingAndroidJson;
            _pendingAndroidJson = null;
            StartCoroutine(SpawnFromAndroid(json));
        }

        if (!autoConnect || SuppressAutoConnectForTests) return;

        await ConnectWebSocket();
    }

    private async System.Threading.Tasks.Task ConnectWebSocket()
    {
#if !UNITY_EDITOR
        // On Android: check if we have a valid non-localhost IP before attempting connection.
        if (pythonServerIP == "127.0.0.1" || pythonServerIP == "localhost" || string.IsNullOrEmpty(pythonServerIP))
        {
            Debug.Log("[SimManager] Android mode: skipping WebSocket connection. Waiting for SetPythonServerIP() from Android app.");
            Debug.Log("[SimManager] Current IP: " + pythonServerIP);
            return;
        }
#endif

        string url = WebSocketUrl;
        Debug.Log("[SimManager] Connecting to: " + url);

        try
        {
            websocket = new WebSocket(url);

            websocket.OnOpen += () => {
                Debug.Log("[SimManager] WebSocket connected: " + url);
                isReconnecting = false;
            };

            websocket.OnError += (e) => {
                Debug.LogError("[SimManager] WebSocket error: " + e);
            };

            websocket.OnClose += async (code) => {
                Debug.Log("[SimManager] WebSocket closed code: " + code);

                // Only auto-reconnect if we have a real non-localhost IP
                if (pythonServerIP != "127.0.0.1" && pythonServerIP != "localhost" && autoConnect && !isReconnecting)
                {
                    isReconnecting = true;
                    await System.Threading.Tasks.Task.Delay((int)(reconnectDelay * 1000));
                    Debug.Log("[SimManager] Reconnecting...");
                    await ConnectWebSocket();
                }
            };

            websocket.OnMessage += (bytes) => {
                string message = System.Text.Encoding.UTF8.GetString(bytes);
                // WebSocket messages arrive on the main thread via DispatchMessageQueue
                // so we can call ProcessMessage directly here (safe in the Update tick)
                ProcessMessage(message);
            };

            await websocket.Connect();
        }
        catch (Exception e)
        {
            Debug.LogError("[SimManager] Connection failed: " + e.Message);
        }
    }

    void Update()
    {
        _unityIsReady = true;

#if !UNITY_WEBGL || UNITY_EDITOR
        websocket?.DispatchMessageQueue();
#endif

        // If a pending config arrived before Start() completed, process it now
        if (!string.IsNullOrEmpty(_pendingAndroidJson))
        {
            string json = _pendingAndroidJson;
            _pendingAndroidJson = null;
            Debug.Log("[SM] Update: flushing pending Android config.");
            if (activeSpawnCoroutine != null) StopCoroutine(activeSpawnCoroutine);
            activeSpawnCoroutine = StartCoroutine(SpawnFromAndroid(json));
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Message dispatch
    // ─────────────────────────────────────────────────────────────────────────

[System.Serializable]
public class BaseMessage { public string type; }

    private void ProcessMessage(string json)
    {
        var baseMsg = JsonUtility.FromJson<BaseMessage>(json);

        if (baseMsg.type == "config_update") {
            // Check if this update is redundant or stale.
            // If Android has recently sent a config (Flow 1), we trust it over the 
            // server's initial broadcast (Flow 2) to prevent reverting to old counts.
            if (androidConfigReceived)
            {
                Debug.Log("[SM] Config update received via WebSocket, but Android master config is active. Skipping rebuild to prevent stale overwrite.");
                // We keep Android Master until the next time ReceiveConfigFromAndroid is called
                return;
            }

            EnsureSpawner();
            if (spawner != null)
            {
                Debug.Log("[SM] Config update received — rebuilding scene");
                spawner.BuildFactory(json);
            }
            return;
        }

        if (baseMsg.type == "state_update") {
            WSStateUpdate update = JsonUtility.FromJson<WSStateUpdate>(json);
            UpdateMachines(update);
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // State update → machine visual update
    // ─────────────────────────────────────────────────────────────────────────

    private void UpdateMachines(WSStateUpdate update)
    {
        if (update == null || update.stations == null) return;

        foreach (var metric in update.stations)
        {
            bool isBottleneck = false;
            if (update.bottleneck_ids != null)
            {
                foreach (int bId in update.bottleneck_ids)
                {
                    if (bId == metric.station_id) { isBottleneck = true; break; }
                }
            }

            if (!stationMachines.TryGetValue(metric.station_id, out var machines))
            {
                // Fallback: search the scene
                machines = new List<MachineVisual>(
                    FindObjectsByType<MachineVisual>(FindObjectsSortMode.None));
                machines.RemoveAll(mv => mv == null || mv.stationId != metric.station_id);
                if (machines.Count > 0)
                    stationMachines[metric.station_id] = machines;
            }

            if (machines == null || machines.Count == 0) continue;

            // Split queue across parallel machines
            int queuePerMachine = Mathf.CeilToInt((float)metric.queue_length / machines.Count);

            foreach (var mv in machines)
            {
                if (mv == null) continue;
                mv.UpdateState(metric.utilization, queuePerMachine, isBottleneck, metric.status);
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Public registration API
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>Register a machine visual under its station ID.</summary>
    public void RegisterMachine(int stationId, int machineIndex, MachineVisual mv)
    {
        if (mv == null) return;
        if (!stationMachines.TryGetValue(stationId, out var list))
        {
            list = new List<MachineVisual>();
            stationMachines[stationId] = list;
        }
        if (!list.Contains(mv)) list.Add(mv);
    }

    /// <summary>Alias: kept for backwards compatibility with old MachineSpawner calls.</summary>
    public void RegisterStation(int stationId, MachineVisual mv) =>
        RegisterMachine(stationId, 0, mv);

    /// <summary>Clear station registry (called before scene rebuild).</summary>
    public void ClearAllStations() => stationMachines.Clear();

    /// <summary>Alias kept for backwards compatibility.</summary>
    public void ClearStations() => ClearAllStations();

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    private void EnsureSpawner()
    {
        if (spawner != null) return;

        spawner = FindFirstObjectByType<MachineSpawner>();

        if (spawner == null)
        {
            Debug.LogError("[SM] EnsureSpawner: No" +
                " MachineSpawner found in scene!");
        }
    }

    private async void OnApplicationQuit()
    {
        isReconnecting = true; // Stop reconnection attempts
        if (websocket != null && websocket.State == WebSocketState.Open)
            await websocket.Close();
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Coroutine: deferred BuildFactory with spawner retry loop
    // Waits up to 10 s for MachineSpawner to become available,
    // then calls BuildFactory on the main thread.
    // ─────────────────────────────────────────────────────────────────────────

    private IEnumerator SpawnFromAndroid(string json)
    {
        Debug.Log("[SM] SpawnFromAndroid: coroutine started on frame " + Time.frameCount);

        // Retry loop — MachineSpawner.Start() may not have run yet
        // if this coroutine fires very early. Poll every 0.5 s.
        int attempts = 0;
        while (spawner == null && attempts < 20) // 20 × 0.5 s = 10 s max
        {
            EnsureSpawner();
            if (spawner == null)
            {
                Debug.LogWarning("[SM] SpawnFromAndroid: spawner null — waiting... attempt=" + attempts);
                yield return new WaitForSeconds(0.5f);
                attempts++;
            }
        }

        if (spawner == null)
        {
            Debug.LogError(
                "[SM] FATAL: MachineSpawner not found in scene after " +
                (attempts * 0.5f).ToString("F0") + " s. " +
                "Check that a GameObject with MachineSpawner component exists.");
            yield break;
        }

        Debug.Log("[SM] Spawner ready: " + spawner.gameObject.name);

        // One frame of safety — ensures all Awake/Start are done
        yield return null;

        // Android sends raw FactoryConfig JSON; wrap it so BuildFactory
        // ExtractConfig() can parse the nested 'config' object correctly.
        string wrapped = "{\"type\":\"config_update\",\"config\":" + json + "}";

        Debug.Log("[SM] Calling BuildFactory... (jsonLen=" + wrapped.Length + ")");

        try
        {
            spawner.BuildFactory(wrapped);
            Debug.Log("[SM] BuildFactory returned OK.");
        }
        catch (System.Exception e)
        {
            Debug.LogError("[SM] BuildFactory threw exception: " + e.Message + "\n" + e.StackTrace);
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Android Integration - Called via UnitySendMessage
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Called from Android via UnitySendMessage.
    /// UnitySendMessage always executes on the Unity main thread,
    /// so it is safe to start a Coroutine here directly.
    /// We use a one-frame deferred Coroutine so that all Awake/Start
    /// initialization (factoryParent, prefabs, etc.) is guaranteed complete
    /// before BuildFactory() runs — even if Android sends the JSON very
    /// quickly (e.g. 1.5 s after launch, before the first Update tick).
    /// </summary>
    public void ReceiveConfigFromAndroid(string json)
    {
        Debug.Log(
            "[SM] ReceiveConfigFromAndroid." +
            " len=" + (json != null ? json.Length.ToString() : "NULL") +
            " — REBUILDING factory with Android counts.");

        if (string.IsNullOrEmpty(json))
        {
            Debug.LogError("[SM] Empty config. Ignoring.");
            return;
        }

        // Mark Android as the master source for the layout.
        // This prevents the WebSocket from reverting machines to old counts.
        androidConfigReceived = true;

        // Store new config — overwrite old
        _pendingAndroidJson = json;

        // Cancel any existing spawn coroutine properly using the handle
        if (activeSpawnCoroutine != null) StopCoroutine(activeSpawnCoroutine);

        activeSpawnCoroutine = StartCoroutine(SpawnFromAndroid(json));
    }

    /// <summary>
    /// Called from Android via UnitySendMessage.
    /// Receives simulation results (station metrics) from Android's SharedViewModel.
    /// JSON format: [{"id":1,"name":"Station","utilization":0.85,"queue":5,"bni":0.72,"is_bottleneck":true},...]
    /// </summary>
    public void ReceiveStationData(string json)
    {
        Debug.Log("[Unity] ReceiveStationData: " + 
            (json.Length > 100 ? json.Substring(0, 100) + "..." : json));
        
        try
        {
            // Unity JsonUtility cannot deserialize arrays directly - wrap in object
            string wrapped = "{\"items\":" + json + "}";
            StationMetricList list = JsonUtility.FromJson<StationMetricList>(wrapped);
            
            if (list?.items == null)
            {
                Debug.LogError("[Unity] Station parse failed - null list");
                return;
            }

            foreach (var s in list.items)
            {
                UpdateStationFromAndroid(s);
            }
        }
        catch (Exception e)
        {
            Debug.LogError("[Unity] ReceiveStationData error: " + e.Message);
        }
    }

    /// <summary>
    /// Called from Android via UnitySendMessage.
    /// Switches station labels between English and Tamil.
    /// </summary>
    public void SetLanguage(string lang)
    {
        currentLanguage = lang;
        Debug.Log("[Unity] Language set to: " + lang);
        
        // Refresh all visible labels
        foreach (var kvp in stationMachines)
        {
            foreach (var mv in kvp.Value)
            {
                if (mv != null) mv.RefreshLabel(lang);
            }
        }
    }

    /// <summary>
    /// Called from Android via UnitySendMessage.
    /// Android sends Python server IP as plain string.
    /// Example: "192.168.1.100"
    /// </summary>
    public void SetPythonServerIP(string ip)
    {
        if (string.IsNullOrEmpty(ip)) return;

        string trimmed = ip.Trim();

        // Reject localhost — that is PC only
        if (trimmed == "127.0.0.1" ||
            trimmed == "localhost")
        {
            Debug.LogWarning(
                "[SimManager] Rejected localhost IP." +
                " Android cannot connect to 127.0.0.1." +
                " Send your PC local network IP instead." +
                " Example: 192.168.1.100");
            return;
        }

        pythonServerIP = trimmed;
        Debug.Log("[SimManager] IP set to: "
            + pythonServerIP);
        Debug.Log("[SimManager] Connecting to: "
            + WebSocketUrl);

        // Close existing connection if any
        if (websocket != null)
        {
            websocket.Close();
            websocket = null;
        }

        // Now connect with real IP
        _ = ConnectWebSocket();
    }

    public string currentLanguage = "en";

    /// <summary>Update a single station from Android simulation data.</summary>
    private void UpdateStationFromAndroid(StationMetric s)
    {
        if (!stationMachines.TryGetValue(s.id, out var machines))
        {
            Debug.LogWarning("[Unity] No machine for station " + s.id);
            return;
        }

        int queuePerMachine = Mathf.CeilToInt((float)s.queue / machines.Count);
        
        foreach (var mv in machines)
        {
            if (mv == null) continue;
            mv.UpdateStatus(s.utilization, queuePerMachine, s.status, s.is_bottleneck, currentLanguage);
            mv.stationName = s.name;
            mv.stationNameTa = s.name_ta;
        }
        
        Debug.Log($"[Unity] Station {s.id} → util={s.utilization:F2} bn={s.is_bottleneck}");
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Station Metric - matches Android StationMetric data class
// ─────────────────────────────────────────────────────────────────────────────

[System.Serializable]
public class StationMetric
{
    public int id;
    public string name;
    public string name_ta;
    public float utilization;
    public int queue;
    public float bni;
    public bool is_bottleneck;
    public string status = "running";
}

[System.Serializable]
public class StationMetricList
{
    public StationMetric[] items;
}
