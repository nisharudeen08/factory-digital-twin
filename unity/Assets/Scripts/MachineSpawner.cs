using System.Collections.Generic;
using UnityEngine;
using TMPro;


public class MachineSpawner : MonoBehaviour
{
    [Header("Required")]
    public SimulationManager simManager;
    public Transform         factoryParent;
    public string            configPath    = "";

    [Header("Grid Spacing")]
    public float machineSpacing = 15f;
    public float machineStep    = 12f;
    public float stationSpacingMultiplier = 0.7f;
    [Header("Factory Building")]
    public bool  spawnBuilding   = true;
    public float wallHeight      = 14f;
    public float wallThickness   = 0.5f;
    public float wallMargin      = 3f;
    public float roofMargin      = 1f;
    public Color wallColor       = new Color(0.75f, 0.75f, 0.70f);
    public Color roofColor       = new Color(0.35f, 0.40f, 0.35f);
    public Material wallMaterial = null;
    public Material roofMaterial = null;

    public float floorMargin    = 10f;

    [Header("Machine Sizing")]
    public float   targetMachineHeight = 3.0f;
    public bool    enableAutoSize      = true;
    public Vector3 sizeMultiplier      = new Vector3(0.8f, 1.0f, 0.8f);

    [Header("Rotation — applies to ALL machines")]
    public Vector3 machineGlobalRotation = new Vector3(0f, 0f, 0f);

    [Header("Lathe — separate rotation fix")]
    public Vector3 latheRotationOffset  = new Vector3(0f, 90f, 0f);
    public Vector3 latheScaleMultiplier = new Vector3(1.0f, 1.0f, 1.0f);
    [Header("Drill — separate rotation fix")]
    public Vector3 drillRotationOffset  = new Vector3(-90f, 0f, 0f);
    public Vector3 drillScaleMultiplier = new Vector3(0.1f, 0.1f, 0.1f);




    [Header("Prefabs")]
    public GameObject lathePrefab;
    public GameObject cncPrefab;
    public GameObject drillPrefab;
    public GameObject bandSawPrefab;
    public GameObject weldPrefab;
    public GameObject grindingPrefab;
    public GameObject qcPrefab;
    public GameObject floorPrefab;
    public Material   floorMaterial;
    public float      machineLightIntensity = 1f;



    [Header("Debug")]
    public bool rebuildNow = false;

    private Dictionary<string, GameObject> prefabMap;

    void Awake()  
    { 
        // Resolve factoryParent from Inspector, or find "Factory" GameObject
        if (factoryParent == null)
        {
            GameObject f = GameObject.Find("Factory");
            if (f != null)
            {
                factoryParent = f.transform;
                Debug.Log("[Spawner] Awake(): factoryParent resolved via Find('Factory'): " + f.name);
            }
            else
            {
                Debug.LogError("[Spawner] Awake(): factoryParent is NULL and no 'Factory' GameObject found in scene! Assign it in the Inspector.");
            }
        }
        else
        {
            Debug.Log("[Spawner] Awake(): factoryParent is: " + factoryParent.name);
        }

        // Resolve simManager if not assigned in Inspector
        if (simManager == null)
        {
            simManager = SimulationManager.Instance
                ?? FindFirstObjectByType<SimulationManager>();
            if (simManager != null)
                Debug.Log("[Spawner] Awake(): simManager resolved via FindFirstObjectByType.");
            else
                Debug.LogWarning("[Spawner] Awake(): simManager is NULL. Machine registration will be skipped.");
        }

        BuildPrefabMap();
        Debug.Log("[Spawner] Awake() complete — prefab map built.");
        Debug.Log($"[Spawner] Lathe prefab assigned: {(lathePrefab != null ? lathePrefab.name : "NULL")}");
        Debug.Log($"[Spawner] CNC   prefab assigned: {(cncPrefab != null ? cncPrefab.name : "NULL")}");
        Debug.Log($"[Spawner] Drill prefab assigned: {(drillPrefab != null ? drillPrefab.name : "NULL")}");
        Debug.Log($"[Spawner] Grinding prefab: {(grindingPrefab != null ? grindingPrefab.name : "NULL")}");
    }

    void Start()
    {
        Debug.Log("[Spawner] Start() called. Platform: " +
            Application.platform.ToString());

    #if UNITY_EDITOR
        Debug.Log("[Spawner] EDITOR MODE - attempting file load.");
        if (!string.IsNullOrEmpty(configPath) &&
            System.IO.File.Exists(configPath))
        {
            string raw = System.IO.File.ReadAllText(configPath);
            BuildFactory(raw);
        }
        else
        {
            Debug.Log("[Spawner] No config file." +
                " Waiting for ReceiveConfigFromAndroid().");
        }
    #else
        Debug.Log("[Spawner] ANDROID MODE.");
        Debug.Log("[Spawner] Skipping file load.");
        Debug.Log("[Spawner] Waiting for Android to call" +
            " ReceiveConfigFromAndroid()...");

        // Validate critical references early on Android so issues
        // show up in Logcat before BuildFactory is called
        ValidateReferences();
    #endif
    }

    /// <summary>
    /// Validate all Inspector-assigned references and log errors for each
    /// missing one. Called at startup on Android to surface issues early.
    /// </summary>
    private void ValidateReferences()
    {
        bool ok = true;

        if (factoryParent == null)
        {
            Debug.LogError("[Spawner] VALIDATE: factoryParent is NULL! " +
                "Machines cannot be spawned. Assign 'Factory' Transform in Inspector.");
            ok = false;
        }
        else
        {
            Debug.Log("[Spawner] VALIDATE: factoryParent OK → " + factoryParent.name);
        }

        if (simManager == null)
        {
            Debug.LogWarning("[Spawner] VALIDATE: simManager is NULL. " +
                "Machine state updates will not work.");
        }
        else
        {
            Debug.Log("[Spawner] VALIDATE: simManager OK → " + simManager.name);
        }

        // Prefab checks
        int nullPrefabs = 0;
        if (lathePrefab    == null) { Debug.LogWarning("[Spawner] VALIDATE: lathePrefab is NULL.");    nullPrefabs++; }
        if (cncPrefab      == null) { Debug.LogWarning("[Spawner] VALIDATE: cncPrefab is NULL.");      nullPrefabs++; }
        if (drillPrefab    == null) { Debug.LogWarning("[Spawner] VALIDATE: drillPrefab is NULL.");    nullPrefabs++; }
        if (bandSawPrefab  == null) { Debug.LogWarning("[Spawner] VALIDATE: bandSawPrefab is NULL.");  nullPrefabs++; }
        if (weldPrefab     == null) { Debug.LogWarning("[Spawner] VALIDATE: weldPrefab is NULL.");     nullPrefabs++; }
        if (grindingPrefab == null) { Debug.LogWarning("[Spawner] VALIDATE: grindingPrefab is NULL."); nullPrefabs++; }

        if (nullPrefabs == 0)
            Debug.Log("[Spawner] VALIDATE: all prefabs OK.");
        else
            Debug.LogWarning($"[Spawner] VALIDATE: {nullPrefabs} prefab(s) are NULL. Fallback cubes will be used.");

        if (ok)
            Debug.Log("[Spawner] VALIDATE: All critical references are valid. Ready for BuildFactory.");
    }

    void Update()
    {
        if (!rebuildNow) return;
        rebuildNow = false;
        Start();
    }

    // ── PUBLIC — called by SimulationManager ──────────────────────────────
    public void BuildFactory(string json)
    {
        Debug.Log(
            "[Spawner] BuildFactory called." +
            " Clearing old factory first.");

        // Always clear before rebuild
        // Never skip this step
        ClearFactory();

        // ── Entry banner — visible immediately in Logcat ──────────────────
        Debug.Log(
            "[Spawner] *** BuildFactory called!" +
            " jsonLen=" + (json?.Length.ToString() ?? "NULL"));
        Debug.Log(
            "[Spawner] factoryParent: " +
            (factoryParent != null ? factoryParent.name : "NULL"));
        Debug.Log(
            "[Spawner] lathePrefab: " +
            (lathePrefab != null ? lathePrefab.name : "NULL"));

        // ── Guard: factoryParent ──────────────────────────────────────────
        if (factoryParent == null)
        {
            // Last-ditch attempt to find it
            GameObject f = GameObject.Find("Factory");
            if (f != null)
            {
                factoryParent = f.transform;
                Debug.LogWarning("[Spawner] BuildFactory: factoryParent was NULL, found via GameObject.Find('Factory').");
            }
            else
            {
                Debug.LogError("[Spawner] BuildFactory: ABORTED — factoryParent is NULL and 'Factory' GameObject not found. " +
                    "Assign the Factory transform in the Inspector.");
                return;
            }
        }

        // ── Guard: json ───────────────────────────────────────────────────
        if (string.IsNullOrEmpty(json))
        {
            Debug.LogError("[Spawner] BuildFactory: ABORTED — JSON is null or empty.");
            return;
        }

        // ── Parse config ──────────────────────────────────────────────────
        FactoryConfig cfg = ExtractConfig(json);

        if (cfg == null)
        {
            Debug.LogError("[Spawner] BuildFactory: ABORTED — ExtractConfig returned null. Check JSON format.");
            return;
        }

        if (cfg.stations == null || cfg.stations.Length == 0)
        {
            Debug.LogWarning("[Spawner] BuildFactory: ABORTED — Config has no stations.");
            return;
        }

        Debug.Log($"[Spawner] BuildFactory: factory='{cfg.factory_name}', stations={cfg.stations.Length}");

        // ── Rebuild prefab map (safety: in case Awake didn't run cleanly) ─
        if (prefabMap == null)
        {
            Debug.LogWarning("[Spawner] BuildFactory: prefabMap was null — rebuilding.");
            BuildPrefabMap();
        }

        // Old call removed since we already call it at the top

        // ── Spawn machines ────────────────────────────────────────────────
        int totalMachines = 0;
        int stationIndex  = 0;
        foreach (var s in cfg.stations)
        {
            if (s == null)
            {
                Debug.LogWarning("[Spawner] BuildFactory: null station in config — skipping.");
                continue;
            }

            int count = Mathf.Max(1, s.num_machines);
            totalMachines += count;

            Debug.Log($"[Spawner] SPAWNING station id={s.id} name='{s.name}' icon='{s.icon}' machines={count}");

            for (int j = 0; j < count; j++)
            {
                // Position: machines within a station line up along X-axis
                Vector3 pos = new Vector3(
                    j * machineSpacing,
                    0f,
                    stationIndex * machineStep
                );

                bool multi = count > 1;
                MachineEntry entry = new MachineEntry
                {
                    stationId        = s.id,
                    machineIndex     = j,
                    totalInStation   = count,
                    name             = multi ? $"{s.name} #{j + 1}" : s.name,
                    nameTa           = multi ? $"{s.name_ta} #{j + 1}" : s.name_ta,
                    icon             = (s.icon ?? "generic").ToLower().Trim(),
                    cycleTimeSec     = s.cycle_time_sec,
                    isFirstInStation = (j == 0)
                };

                SpawnMachine(entry, pos);
            }
            stationIndex++;
        }

        // ── Calculate actual machine bounds ──────────────────────────────


        // ── Spawn floor sized to building ─────────────────────────────────


        // ── Spawn building walls + roof ───────────────────────────────────


        // Spawn floor sized to all machines
        if (floorPrefab != null)
        {
            // Find bounds of all spawned machines
            MachineVisual[] allMachines =
                factoryParent
                    .GetComponentsInChildren<MachineVisual>();
            if (allMachines != null &&
                allMachines.Length > 0)
            {
                Bounds fb = new Bounds(
                    allMachines[0].transform.position,
                    Vector3.zero);
                foreach (var mv in allMachines)
                    fb.Encapsulate(
                        mv.transform.position);

                float fw = fb.size.x + wallMargin * 2f;
                float fd = fb.size.z + wallMargin * 2f;
                float cx = fb.center.x;
                float cz = fb.center.z;

                GameObject floor =
                    Instantiate(floorPrefab,
                        factoryParent);
                floor.name = "FactoryFloor";
                floor.transform.localPosition =
                    new Vector3(cx, -0.05f, cz);

                bool isPlane = floorPrefab.name
                    .ToLower().Contains("plane");
                floor.transform.localScale = isPlane
                    ? new Vector3(fw/10f, 1f, fd/10f)
                    : new Vector3(fw, 0.1f, fd);

                if (floorMaterial != null)
                {
                    Renderer fr =
                        floor.GetComponent<Renderer>();
                    if (fr != null)
                    {
                        fr.material = floorMaterial;
                        // Tile the material based on
                        // floor size so texture looks
                        // correct at any factory scale
                        float tileX = fw / 4f;
                        float tileZ = fd / 4f;
                        fr.material.mainTextureScale =
                            new Vector2(tileX, tileZ);
                    }
                }

                Debug.Log(
                    $"[Spawner] Floor spawned:" +
                    $" W={fw:F1} D={fd:F1}");
            }
        }

        // Spawn building around machines
        if (spawnBuilding)
            SpawnBuildingAroundMachines();

        Debug.Log($"[Spawner] Done. Factory '{cfg.factory_name}' — {totalMachines} machines spawned.");

        // ── Refocus camera ────────────────────────────────────────────────
        var camCtrl = FindFirstObjectByType<CameraController>();
        if (camCtrl != null)
            camCtrl.RefocusAfterRebuild();
        else
            Debug.LogWarning("[Spawner] CameraController not found — skipping refocus.");
    }

    // ── Config extraction ─────────────────────────────────────────────────
    FactoryConfig ExtractConfig(string json)
    {
        try
        {
            if (string.IsNullOrEmpty(json))
            {
                Debug.LogError("[Spawner] ExtractConfig: JSON is null/empty.");
                return null;
            }

            int keyIndex = json.IndexOf("\"config\"");
            if (keyIndex < 0)
            {
                // Treat as a raw FactoryConfig JSON
                Debug.Log("[Spawner] ExtractConfig: no 'config' wrapper found — parsing as raw FactoryConfig.");
                FactoryConfig direct = JsonUtility.FromJson<FactoryConfig>(json);
                if (direct == null)
                    Debug.LogError("[Spawner] ExtractConfig: JsonUtility.FromJson returned null for raw FactoryConfig.");
                else
                    Debug.Log($"[Spawner] ExtractConfig (raw): factory='{direct.factory_name}', stations={(direct.stations?.Length ?? 0)}");
                return direct;
            }

            int braceStart = json.IndexOf('{', keyIndex + 8);
            if (braceStart < 0)
            {
                Debug.LogError("[Spawner] ExtractConfig: could not find opening brace after 'config' key.");
                return null;
            }

            int depth = 0, end = braceStart;
            for (int i = braceStart; i < json.Length; i++)
            {
                if (json[i] == '{') depth++;
                else if (json[i] == '}')
                {
                    depth--;
                    if (depth == 0) { end = i; break; }
                }
            }

            if (depth != 0)
            {
                Debug.LogError("[Spawner] ExtractConfig: JSON is malformed — unmatched braces.");
                return null;
            }

            string inner = json.Substring(braceStart, end - braceStart + 1);
            Debug.Log($"[Spawner] ExtractConfig: inner JSON length={inner.Length}");

            FactoryConfig cfg = JsonUtility.FromJson<FactoryConfig>(inner);
            if (cfg == null)
                Debug.LogError("[Spawner] ExtractConfig: JsonUtility.FromJson returned null for wrapped FactoryConfig.");
            else
                Debug.Log($"[Spawner] ExtractConfig (wrapped): factory='{cfg.factory_name}', stations={(cfg.stations?.Length ?? 0)}");
            return cfg;
        }
        catch (System.Exception e)
        {
            Debug.LogError("[Spawner] ExtractConfig exception: " + e.Message + "\n" + e.StackTrace);
            return null;
        }
    }

    // (ExpandStations method removed)


    // ── Spawn one machine ─────────────────────────────────────────────────
    void SpawnMachine(MachineEntry m, Vector3 pos)
    {
        // Guard: factoryParent must be valid
        if (factoryParent == null)
        {
            Debug.LogError($"[Spawner] SpawnMachine: factoryParent is NULL — cannot spawn '{m.icon}' for station {m.stationId}.");
            return;
        }

        // Guard: entry must be valid
        if (m == null)
        {
            Debug.LogError("[Spawner] SpawnMachine: MachineEntry is null.");
            return;
        }

        Debug.Log($"[Spawner] SpawnMachine: icon='{m.icon}' station={m.stationId} index={m.machineIndex} pos={pos}");

        GameObject prefab = ResolvePrefab(m.icon);
        GameObject obj;

        if (prefab != null)
        {
            Debug.Log($"[Spawner] Using prefab: {prefab.name}");
            obj = Instantiate(prefab, factoryParent);
        }
        else
        {
            Debug.LogWarning($"[Spawner] No prefab for '{m.icon}' (no generic fallback). Using primitive cube.");
            obj = CreateFallback3DMachine($"S{m.stationId}_{m.icon}_Fallback");
            if (obj != null) obj.transform.SetParent(factoryParent, false);
        }

        if (obj == null)
        {
            Debug.LogError($"[Spawner] Failed to instantiate/create machine for '{m.icon}' station {m.stationId}.");
            return;
        }

        // Sanity: confirm parent
        string pName = (factoryParent != null ? factoryParent.name : "NULL");
        Debug.Log($"[Spawner] Instantiated '{obj.name}' — parent: {pName}, localPos: {obj.transform.localPosition}");

        // Flat-prefab guard — only for non-lathe
        bool isLathe = m.icon == "lathe";
        bool isDrill = m.icon == "drill";


        if (isLathe)
        {
            Debug.Log($"[Spawner] SPAWNING LATHE at station {m.stationId}");
        }

        if (!isLathe)
        {
            Renderer[] rends = obj.GetComponentsInChildren<Renderer>();
            bool flat = rends.Length == 0;
            if (!flat)
            {
                Bounds cb = rends[0].bounds;
                foreach (var r in rends)
                    cb.Encapsulate(r.bounds);
                flat = cb.size.y < 0.1f;
            }
            if (flat)
            {
                Debug.LogWarning($"[Spawner] Prefab '{obj.name}' appears flat (y<0.1). Using fallback 3D cube.");
                DestroyImmediate(obj, true);
                obj = CreateFallback3DMachine(
                    $"S{m.stationId}_{m.icon}" +
                    $"_M{m.machineIndex+1}");
                if (obj == null)
                {
                    Debug.LogError($"[Spawner] CreateFallback3DMachine returned null for '{m.icon}'.");
                    return;
                }
                obj.transform.SetParent(factoryParent, false);
            }
        }

        obj.name = $"S{m.stationId}_{m.icon}_M{m.machineIndex + 1}";

        if (isLathe)
        {
            obj.transform.localPosition = pos;
            CenterAndGround(obj);
        }
        else if (isDrill)
        {
            obj.transform.localPosition = pos;
            obj.transform.localRotation =
                Quaternion.Euler(drillRotationOffset);
            obj.transform.localScale =
                drillScaleMultiplier;
            CenterAndGround(obj);
        }
        else
        {
            obj.transform.localPosition = Vector3.zero;
            obj.transform.localRotation = Quaternion.Euler(machineGlobalRotation);
            obj.transform.localScale    = Vector3.one;

            if (enableAutoSize)
            {
                Bounds b = GetEffectiveBounds(obj);
                float h = b.size.y;
                if (h > 0.01f)
                {
                    float factor = targetMachineHeight / h;
                    obj.transform.localScale = new Vector3(factor, factor, factor);
                    obj.transform.localScale = Vector3.Scale(obj.transform.localScale, sizeMultiplier);
                }
                else
                {
                    Debug.LogWarning($"[Spawner] AutoSize: bounds height={h:F4} too small for '{obj.name}', using sizeMultiplier directly.");
                    obj.transform.localScale = sizeMultiplier;
                }
            }
            else
            {
                obj.transform.localScale = sizeMultiplier;
            }

            obj.transform.localPosition = pos;
            CenterAndGround(obj);
        }

        Debug.Log($"[Spawner] '{obj.name}' placed at localPos={obj.transform.localPosition} scale={obj.transform.localScale}");

        // ── MachineVisual ──────────────────────────────────────────────────
        MachineVisual mv =
            obj.GetComponent<MachineVisual>()
            ?? obj.AddComponent<MachineVisual>();
        
        if (mv == null)
        {
            Debug.LogError($"[Spawner] Failed to get/add MachineVisual on '{obj.name}'.");
            return;
        }

        mv.stationId        = m.stationId;
        mv.machineIndex     = m.machineIndex;
        mv.stationName      = m.name;
        mv.stationNameTa    = m.nameTa;
        mv.numMachinesTotal = m.totalInStation;
        mv.showLabel        = m.isFirstInStation;

        // Fix light intensity on spawned machine
        Light[] lights =
            obj.GetComponentsInChildren<Light>();
        foreach (var l in lights)
        {
            if (l != null)
                l.intensity = machineLightIntensity;
        }
        if (lights.Length > 0)
            Debug.Log(
                $"[Spawner] Fixed {lights.Length}" +
                $" lights on '{obj.name}'" +
                $" intensity={machineLightIntensity}");

        Debug.Log($"[Spawner] Registering — station={m.stationId} index={m.machineIndex}");

        if (simManager != null)
            simManager.RegisterMachine(m.stationId, m.machineIndex, mv);
        else
            Debug.LogWarning($"[Spawner] simManager is NULL — skipping RegisterMachine for station {m.stationId}.");
    }

    // ── Prefab resolution ─────────────────────────────────────────────────
    GameObject ResolvePrefab(string icon)
    {
        if (prefabMap == null)
        {
            Debug.LogWarning("[Spawner] ResolvePrefab: prefabMap was null — rebuilding.");
            BuildPrefabMap();
        }
        
        if (prefabMap.TryGetValue(icon, out var p) && p != null) 
            return p;
        
        Debug.LogWarning($"[Spawner] Prefab not found for icon '{icon}', using grinding/generic fallback");
        return (grindingPrefab != null) ? grindingPrefab : null;
    }

    void BuildPrefabMap()
    {
        // Use Unity-safe null checks instead of ?? for GameObjects
        GameObject def = (grindingPrefab != null) ? grindingPrefab : null;

        prefabMap = new Dictionary<string, GameObject>
        {
            { "lathe",       (lathePrefab != null)   ? lathePrefab   : def },
            { "milling",     (cncPrefab != null)     ? cncPrefab     : def },
            { "cnc",         (cncPrefab != null)     ? cncPrefab     : def },
            { "milling/cnc", (cncPrefab != null)     ? cncPrefab     : def },
            { "drill",       (drillPrefab != null)   ? drillPrefab   : def },
            { "band_saw",    (bandSawPrefab != null) ? bandSawPrefab : def },
            { "bandsaw",     (bandSawPrefab != null) ? bandSawPrefab : def },
            { "weld",        (weldPrefab != null)    ? weldPrefab    : def },
            { "welding",     (weldPrefab != null)    ? weldPrefab    : def },
            { "grind",       def },
            { "grinding",    def },
            { "paint",       def },
            { "painting",    def },
            { "generic",     def },
            { "wipbox",      def },
            { "qc",          (qcPrefab != null) ? qcPrefab : def },
            { "qc_inspection", (qcPrefab != null) ? qcPrefab : def },
            { "inspection",  (qcPrefab != null) ? qcPrefab : def },
        };

        Debug.Log("[Spawner] Prefab map built.");
    }

    // ── Floor ─────────────────────────────────────────────────────────────
    void SpawnFloor(int cols, int rows)
    {
        if (floorPrefab == null)
        {
            Debug.LogWarning("[Spawner] SpawnFloor: floorPrefab is NULL — skipping floor.");
            return;
        }

        if (factoryParent == null)
        {
            Debug.LogError("[Spawner] SpawnFloor: factoryParent is NULL — cannot spawn floor.");
            return;
        }

        float w  = (cols - 1) * machineSpacing
                   + floorMargin * 2f;
        float d  = (rows - 1) * machineStep
                   + floorMargin * 2f;
        float cx = (cols - 1) * machineSpacing / 2f;
        float cz = (rows - 1) * machineStep    / 2f;

        GameObject floor =
            Instantiate(floorPrefab, factoryParent);
        floor.name = "FactoryFloor";
        floor.transform.localPosition =
            new Vector3(cx, -0.05f, cz);

        bool isPlane =
            floorPrefab.name.ToLower().Contains("plane");
        floor.transform.localScale = isPlane
            ? new Vector3(w / 10f, 1f, d / 10f)
            : new Vector3(w, 0.1f, d);
    }

    void SpawnBuildingAroundMachines()
    {
        if (factoryParent == null) return;
        // Get ALL renderers inside factory
        // to find true visual bounds
        // including machine models
        Renderer[] renderers =
            factoryParent
                .GetComponentsInChildren<Renderer>();

        if (renderers == null ||
            renderers.Length == 0)
        {
            Debug.LogWarning(
                "[Spawner] SpawnBuilding:" +
                " no renderers found.");
            return;
        }

        // Convert world bounds to LOCAL space
        // of factoryParent so walls align
        // with machines correctly
        Bounds b = new Bounds(
            factoryParent.InverseTransformPoint(
                renderers[0].bounds.center),
            Vector3.zero);

        foreach (var r in renderers)
        {
            if (r == null) continue;
            // Convert each renderer world
            // position to local space
            Vector3 localMin = factoryParent
                .InverseTransformPoint(r.bounds.min);
            Vector3 localMax = factoryParent
                .InverseTransformPoint(r.bounds.max);
            b.Encapsulate(localMin);
            b.Encapsulate(localMax);
        }

        // Add margin so machines have
        // breathing room from walls
        float minX = b.min.x - wallMargin;
        float maxX = b.max.x + wallMargin;
        float minZ = b.min.z - wallMargin;
        float maxZ = b.max.z + wallMargin;

        // Roof height must clear tallest machine
        // Add roofMargin above highest point
        float roofY = b.max.y + roofMargin;
        // Also enforce minimum wall height
        roofY = Mathf.Max(roofY, wallHeight);

        float buildingW = maxX - minX;
        float buildingD = maxZ - minZ;
        float centerX   = (minX + maxX) / 2f;
        float centerZ   = (minZ + maxZ) / 2f;
        float wallCenterY = roofY / 2f;

        Debug.Log(
            $"[Spawner] Building:" +
            $" W={buildingW:F1}" +
            $" D={buildingD:F1}" +
            $" H={roofY:F1}" +
            $" machines inside guaranteed.");

        // Create building parent
        GameObject building =
            new GameObject("Factory_Building");
        building.transform.SetParent(
            factoryParent, false);

        // Wall material
        Material wMat = wallMaterial != null
            ? wallMaterial
            : new Material(
                Shader.Find(
                    "Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard"));
        if (wallMaterial == null)
            wMat.color = wallColor;

        // Roof material
        Material rMat = roofMaterial != null
            ? roofMaterial
            : new Material(
                Shader.Find(
                    "Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard"));
        if (roofMaterial == null)
            rMat.color = roofColor;

        // NORTH wall
        MakeWall(building.transform,
            new Vector3(centerX, wallCenterY, maxZ),
            new Vector3(buildingW + wallThickness * 2f,
                roofY, wallThickness),
            "Wall_North", wMat);

        // SOUTH wall
        MakeWall(building.transform,
            new Vector3(centerX, wallCenterY, minZ),
            new Vector3(buildingW + wallThickness * 2f,
                roofY, wallThickness),
            "Wall_South", wMat);

        // EAST wall
        MakeWall(building.transform,
            new Vector3(maxX, wallCenterY, centerZ),
            new Vector3(wallThickness,
                roofY, buildingD),
            "Wall_East", wMat);

        // WEST wall
        MakeWall(building.transform,
            new Vector3(minX, wallCenterY, centerZ),
            new Vector3(wallThickness,
                roofY, buildingD),
            "Wall_West", wMat);

        // ROOF — sits exactly on top of walls
        MakeWall(building.transform,
            new Vector3(centerX,
                roofY + wallThickness / 2f,
                centerZ),
            new Vector3(
                buildingW + wallThickness * 2f,
                wallThickness,
                buildingD + wallThickness * 2f),
            "Roof", rMat);

        // ROOF BEAMS for visual detail
        int beamCount = Mathf.Max(2,
            Mathf.RoundToInt(buildingD / 10f));
        for (int i = 0; i <= beamCount; i++)
        {
            float bz = Mathf.Lerp(
                minZ, maxZ,
                (float)i / beamCount);
            GameObject beam =
                GameObject.CreatePrimitive(
                    PrimitiveType.Cube);
            beam.name = $"Beam_{i}";
            beam.transform.SetParent(
                building.transform, false);
            beam.transform.localPosition =
                new Vector3(centerX,
                    roofY - 0.4f, bz);
            beam.transform.localScale =
                new Vector3(buildingW, 0.4f, 0.4f);
            var br = beam.GetComponent<Renderer>();
            if (br != null)
            {
                Material bm = new Material(
                    Shader.Find(
                        "Universal Render Pipeline/Lit")
                    ?? Shader.Find("Standard"));
                bm.color = new Color(
                    0.2f, 0.2f, 0.2f);
                br.material = bm;
            }
        }

        Debug.Log(
            "[Spawner] Building complete:" +
            " 4 walls + roof + beams.");
    }

    void MakeWall(
        Transform parent,
        Vector3 position,
        Vector3 scale,
        string wallName,
        Material mat)
    {
        GameObject wall =
            GameObject.CreatePrimitive(
                PrimitiveType.Cube);
        wall.name = wallName;
        wall.transform.SetParent(parent, false);
        wall.transform.localPosition = position;
        wall.transform.localScale    = scale;
        var wr = wall.GetComponent<Renderer>();
        if (wr != null) wr.material = mat;
    }

    // ── Clear factory ─────────────────────────────────────────────────────
    void ClearFactory()
    {
        if (factoryParent == null)
        {
            Debug.LogWarning("[Spawner] ClearFactory: factoryParent is null.");
            return;
        }

        // Collect children first to avoid modification issues
        List<GameObject> toDestroy = new List<GameObject>();
        foreach (Transform child in factoryParent)
        {
            toDestroy.Add(child.gameObject);
        }

        Debug.Log($"[Spawner] ClearFactory: cleaning up {toDestroy.Count} objects.");

        foreach (var child in toDestroy)
        {
            // Detach immediately so they aren't found by GetComponentsInChildren during the same frame rebuild
            child.transform.SetParent(null);
            Destroy(child);
        }

        // Also clear registered machines in SimManager
        if (simManager != null) 
            simManager.ClearAllStations();
    }

    // ── Fallback 3D machine ───────────────────────────────────────────────
    static GameObject CreateFallback3DMachine(string n)
    {
        GameObject root = new GameObject(n);

        GameObject body =
            GameObject.CreatePrimitive(PrimitiveType.Cube);
        body.name = "Body";
        body.transform.SetParent(root.transform, false);
        body.transform.localPosition =
            new Vector3(0f, 0.5f, 0f);
        body.transform.localScale =
            new Vector3(1.0f, 1.0f, 0.8f);

        GameObject panel =
            GameObject.CreatePrimitive(PrimitiveType.Cube);
        panel.name = "ControlPanel";
        panel.transform.SetParent(root.transform, false);
        panel.transform.localPosition =
            new Vector3(0f, 1.1f, -0.3f);
        panel.transform.localScale =
            new Vector3(0.6f, 0.15f, 0.15f);

        GameObject base3D =
            GameObject.CreatePrimitive(PrimitiveType.Cube);
        base3D.name = "Base";
        base3D.transform.SetParent(root.transform, false);
        base3D.transform.localPosition =
            new Vector3(0f, 0.05f, 0f);
        base3D.transform.localScale =
            new Vector3(1.15f, 0.1f, 0.95f);

        return root;
    }

    // ── Bounds helpers ────────────────────────────────────────────────────
    Bounds GetEffectiveBounds(GameObject root)
    {
        if (root == null)
            return new Bounds(Vector3.zero, Vector3.one * 0.1f);

        Renderer[] rs =
            root.GetComponentsInChildren<Renderer>(false);
        Bounds b     = new Bounds();
        bool   first = true;
        foreach (var r in rs)
        {
            if (r == null) continue;
            string nm = r.name.ToLower();
            if (nm.Contains("label") ||
                nm.Contains("text")  ||
                nm.Contains("arrow") ||
                nm.Contains("gizmo") ||
                nm.Contains("badge")) continue;
            if (first) { b = r.bounds; first = false; }
            else b.Encapsulate(r.bounds);
        }
        if (first)
            return new Bounds(
                root.transform.position,
                Vector3.one * 0.1f);
        return b;
    }

    void CenterAndGround(GameObject root)
    {
        if (root == null) return;
        Bounds b = GetEffectiveBounds(root);
        if (b.size.sqrMagnitude < 0.001f) return;
        Vector3 bottomCenter =
            new Vector3(b.center.x, b.min.y, b.center.z);
        Vector3 offset =
            root.transform.position - bottomCenter;
        foreach (Transform child in root.transform)
        {
            if (child != null)
                child.position += offset;
        }
    }

    // ── FACTORY BUILDING SPANNER ──────────────────────────────────────────


}

class MachineEntry
{
    public int    stationId;
    public int    machineIndex;
    public int    totalInStation;
    public string name;
    public string nameTa;
    public string icon;
    public float  cycleTimeSec;
    public bool   isFirstInStation;
}
