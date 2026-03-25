using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.Serialization;

public class MachineVisual : MonoBehaviour
{
    private const float MediumUtilizationThreshold = 0.15f;
    private const float HighUtilizationThreshold = 0.30f;
    private const float CriticalUtilizationThreshold = 0.40f;
    private const float DefaultLabelHeight = 1.6f;

    public bool IsBottleneck
        { get; private set; }

    public int stationId;
    [FormerlySerializedAs("stationName")]
    public string machineDisplayName;
    public string machineTypeName;
    public Renderer bodyRenderer;
    public TMP_Text labelTMP;
    public SpriteRenderer labelBg;
    public GameObject bottleneckArrow;
    [FormerlySerializedAs("queueStartPoint")]
    public Transform queueParent;
    public GameObject queueBoxPrefab;

    // ── Multi-machine fields (set by MachineSpawner) ──────────────────────
    /// <summary>0-based index of this machine within its station.</summary>
    public int  machineIndex;
    /// <summary>Total parallel machines at this station.</summary>
    public int  numMachinesTotal;
    /// <summary>Only the first machine (machineIndex==0) shows the label.</summary>
    public bool showLabel = true;

    public Material matGreen;
    public Material matAmber;
    public Material matOrange;
    public Material matRed;
    public Material matGray;

    [FormerlySerializedAs("runningMat")]
    [SerializeField] private Material legacyRunningMat;
    [FormerlySerializedAs("brokenMat")]
    [SerializeField] private Material legacyBrokenMat;
    [FormerlySerializedAs("maintenanceMat")]
    [SerializeField] private Material legacyMaintenanceMat;
    [FormerlySerializedAs("idleMat")]
    [SerializeField] private Material legacyIdleMat;

    private Coroutine pulseCoroutine;
    private string cachedMachineName;
    private string cachedMachineTypeName;
    private Renderer[] cachedRenderers;
    private bool hasLiveState;
    private float latestUtilization;
    private int latestQueue;

    // Store current values for label refresh when language changes
    private string currentStatus = "running";
    private bool currentIsBottleneck;
    private string currentLanguage = "en";
    public string stationName;
    public string stationNameTa;

    private void Awake()
    {
        CacheRenderers();
        CacheMachineName();
        CacheMachineTypeName();
    }

    private void Start()
    {
        // Set initial color to Neutral Gray until data arrives
        ApplyColorToAllRenderers(new Color(0.7f, 0.7f, 0.7f));
        RefreshIdentityLabel();
    }

    private void Update()
    {
        // MANUAL TEST: Press 'C' to toggle color to Red
        if (Input.GetKeyDown(KeyCode.C))
        {
            ApplyColorToAllRenderers(Color.red);
            Debug.Log($"[Visual] Manual color test: Applied RED to {gameObject.name}");
            if (labelTMP != null) labelTMP.text = "COLOR TEST";
        }
    }

    public void UpdateStatus(float util, int queue, string status, bool isBottleneck)
    {
        UpdateStatus(util, queue, status, isBottleneck, currentLanguage);
    }

    public void UpdateState(float utilization, int queue, bool isBottleneck, string status)
    {
        UpdateStatus(utilization, queue, status, isBottleneck, currentLanguage);
    }

    public void UpdateState(float util, float queueLength, bool isBottleneck, string status)
    {
        UpdateStatus(util, Mathf.Max(0, Mathf.RoundToInt(queueLength)), status, isBottleneck, currentLanguage);
    }

    /// <summary>
    /// Overload with language parameter for Android integration.
    /// </summary>
    public void UpdateStatus(float utilization, int queue, string status, bool isBottleneck, string lang, int lossCount = 0)
    {
        currentLanguage = lang;
        currentStatus = status;
        currentIsBottleneck = isBottleneck;
        IsBottleneck = isBottleneck;
        latestUtilization = utilization;
        latestQueue = queue;
        hasLiveState = true;
        Debug.Log($"[Visual] S{stationId} received: util={utilization}, status={status}, bottleneck={isBottleneck}");

        if (cachedRenderers == null || cachedRenderers.Length == 0) CacheRenderers();
        EnsureLabelExists();

        // ── Color by status ──────────────────────────────────────────
        StopAllCoroutines();   // stop any existing pulse first

        Color targetColor;

        if (isBottleneck)
        {
            // Absolute Bottleneck -> Pulsing Red
            IsBottleneck = true;
            Debug.Log($"[Visual] S{stationId} BOTTLENECK detected! Pulsing red.");
            StartCoroutine(PulseColor(
                new Color(1.0f, 0.1f, 0.1f),   // Bright Red
                new Color(0.4f, 0.0f, 0.0f)    // Dark Red
            ));
        }
        else
        {
            if (status == "broken" || status == "maintenance")
            {
                // Machine Breakdown -> Dark Gray
                targetColor = new Color(0.2f, 0.2f, 0.2f); 
            }
            else if (utilization >= 0.80f)
            {
                // Critical Load -> Orange
                targetColor = new Color(1.0f, 0.5f, 0.0f);
            }
            else if (utilization >= 0.50f)
            {
                // High Load -> Vivid Yellow
                targetColor = new Color(1.0f, 1.0f, 0.0f);
            }
            else if (status == "idle")
            {
                // Idle -> Light Gray
                targetColor = new Color(0.6f, 0.6f, 0.6f);
            }
            else
            {
                // Normal Running -> Green
                targetColor = new Color(0.0f, 0.8f, 0.2f);
            }

            IsBottleneck = false;
            ApplyColorToAllRenderers(targetColor);
        }

        // Bottleneck Arrow (preserve existing behavior if needed, though color pulse might be enough)
        if (bottleneckArrow != null)
        {
            bottleneckArrow.SetActive(isBottleneck);
            if (isBottleneck) StartCoroutine(PulseArrow());
            else bottleneckArrow.transform.localScale = Vector3.one;
        }

        // Rebuild queue boxes
        if (queueParent != null && queueBoxPrefab != null)
        {
            foreach (Transform t in queueParent) Destroy(t.gameObject);
            for (int i = 0; i < queue; i++)
            {
                Vector3 pos = queueParent.position + Vector3.right * i * 0.4f;
                Instantiate(queueBoxPrefab, pos, Quaternion.identity, queueParent);
            }
        }

        // Label update logic from requirements
        if (labelTMP != null)
        {
            UpdateLabel(utilization, queue, lossCount, lang);
        }
    }

    private void UpdateLabel(float utilPct, int queueLength, int lossCount, string lang)
    {
        if (labelTMP == null) return;

        // Resolve display name based on language
        string displayName = !string.IsNullOrEmpty(stationNameTa) && lang == "ta"
            ? stationNameTa
            : (!string.IsNullOrEmpty(stationName) ? stationName : cachedMachineName);

        // Station name — bold, larger
        string line1 =
            $"<b><size=110%>{displayName}</size></b>";

        // Type line
        string line2 =
            $"<color=#000000>Type: Machine</color>";

        // Values line — bold numbers, dot separator
        string line3 =
            $"<color=#000000>" +
            $"<b>{utilPct * 100f:0}%</b> Util" +
            $"  •  " +
            $"Q: <b>{queueLength}</b>" +
            $"  •  " +
            $"Loss: <b>{lossCount}</b>" +
            $"</color>";

        // Machine count line
        string line4 =
            $"<color=#000000>" +
            $"({numMachinesTotal} machines)" +
            $"</color>";

        labelTMP.text =
            line1 + "\n" +
            line2 + "\n" +
            line3 + "\n" +
            line4;

        labelTMP.color = Color.black;
        labelTMP.fontStyle = FontStyles.Normal;

        // White background semi-transparent
        if (labelBg != null)
        {
            labelBg.color = new Color(1f, 1f, 1f, 0.85f);
        }
    }

    /// <summary>
    /// Refresh the label text when language changes.
    /// Called from SimulationManager.SetLanguage().
    /// </summary>
    public void RefreshLabel(string lang)
    {
        if (labelTMP == null) return;

        // Use Tamil name if language is Tamil and name is available
        string displayName = !string.IsNullOrEmpty(stationNameTa) && lang == "ta"
            ? stationNameTa
            : (!string.IsNullOrEmpty(stationName) ? stationName : cachedMachineName);

        string typeLine = $"Type: {cachedMachineTypeName}";
        string machineInfo = numMachinesTotal > 1 ? $"\n({numMachinesTotal} machines)" : string.Empty;

        if (!hasLiveState)
        {
            labelTMP.text = $"{displayName}\n{typeLine}{machineInfo}";
            return;
        }

        string utilStr = (latestUtilization * 100f).ToString("F0");
        labelTMP.text = $"{displayName}\n{typeLine}\n{utilStr}%  Q:{latestQueue}{machineInfo}";
    }

    public void ConfigureIdentity(string displayName, string typeName)
    {
        machineDisplayName = string.IsNullOrWhiteSpace(displayName) ? gameObject.name : displayName;
        machineTypeName = string.IsNullOrWhiteSpace(typeName) ? "Machine" : typeName;
        cachedMachineName = machineDisplayName;
        cachedMachineTypeName = machineTypeName;

        EnsureLabelExists();
        RefreshIdentityLabel();
    }

    private void CacheRenderers()
    {
        cachedRenderers = GetComponentsInChildren<Renderer>(true);

        if (bodyRenderer == null && cachedRenderers.Length > 0)
        {
            bodyRenderer = cachedRenderers[0];
        }
    }

    private void CacheMachineName()
    {
        if (!string.IsNullOrWhiteSpace(cachedMachineName))
        {
            return;
        }

        if (!string.IsNullOrWhiteSpace(machineDisplayName))
        {
            cachedMachineName = machineDisplayName;
            return;
        }

        if (labelTMP != null && !string.IsNullOrWhiteSpace(labelTMP.text))
        {
            cachedMachineName = labelTMP.text.Split('\n')[0];
            return;
        }

        cachedMachineName = gameObject.name;
    }

    private void CacheMachineTypeName()
    {
        if (!string.IsNullOrWhiteSpace(cachedMachineTypeName))
        {
            return;
        }

        cachedMachineTypeName = string.IsNullOrWhiteSpace(machineTypeName)
            ? "Machine"
            : machineTypeName;
    }

    private void EnsureLabelExists()
    {
        if (labelTMP != null)
        {
            return;
        }

        GameObject labelObject = new GameObject("MachineLabel");
        labelObject.transform.SetParent(transform, false);
        labelObject.transform.localPosition = Vector3.up * GetLabelHeight();
        labelObject.transform.localRotation = Quaternion.identity;
        labelObject.transform.localScale = Vector3.one * 0.18f;

        TextMeshPro textMesh = labelObject.AddComponent<TextMeshPro>();
        if (TMP_Settings.defaultFontAsset != null)
        {
            textMesh.font = TMP_Settings.defaultFontAsset;
        }

        textMesh.alignment = TextAlignmentOptions.Center;
        textMesh.fontSize = 20f;
        textMesh.textWrappingMode = TextWrappingModes.NoWrap; // FIXED TMP WARNING
        textMesh.color = Color.black;
        textMesh.outlineWidth = 0f;

        labelTMP = textMesh;

        // Create background
        GameObject bgObj = GameObject.CreatePrimitive(PrimitiveType.Quad);
        bgObj.name = "Background";
        bgObj.transform.SetParent(labelObject.transform, false);
        bgObj.transform.localPosition = new Vector3(0, 0, 0.01f);
        bgObj.transform.localScale = new Vector3(8f, 4f, 1f);
        DestroyImmediate(bgObj.GetComponent<Collider>());
        labelBg = bgObj.GetComponent<SpriteRenderer>(); 
        if (labelBg == null) 
        {
            // If CreatePrimitive(Quad) doesn't have SpriteRenderer (it has MeshRenderer), 
            // we should use a Sprite instead or just color the MeshRenderer.
            // But the prompt says labelBg.color = ..., which works for MeshRenderer.material.color too.
            // However, SpriteRenderer is more common for 2D labels.
            // I'll add a simple SpriteRenderer.
            DestroyImmediate(bgObj.GetComponent<MeshRenderer>());
            DestroyImmediate(bgObj.GetComponent<MeshFilter>());
            labelBg = bgObj.AddComponent<SpriteRenderer>();
        }
    }

    private float GetLabelHeight()
    {
        CacheRenderers();

        float highestPoint = DefaultLabelHeight;
        foreach (Renderer renderer in cachedRenderers)
        {
            if (renderer == null)
            {
                continue;
            }

            float candidateHeight = renderer.bounds.max.y - transform.position.y + 0.5f;
            if (candidateHeight > highestPoint)
            {
                highestPoint = candidateHeight;
            }
        }

        return highestPoint;
    }

    private void RefreshIdentityLabel()
    {
        if (labelTMP != null)
        {
            labelTMP.text = BuildLabelText();
        }
    }

    private string BuildLabelText()
    {
        // Non-primary machines suppress their label
        if (!showLabel)
        {
            if (labelTMP != null) labelTMP.gameObject.SetActive(false);
            return string.Empty;
        }

        if (labelTMP != null) labelTMP.gameObject.SetActive(true);

        // Keep existing legacy text builder for initial/fallback use
        string displayName = !string.IsNullOrEmpty(stationName) ? stationName : cachedMachineName;
        string typeLine    = $"Type: {cachedMachineTypeName}";
        string machineInfo = numMachinesTotal > 1 ? $"\n({numMachinesTotal} machines)" : string.Empty;

        if (!hasLiveState)
            return $"{displayName}\n{typeLine}{machineInfo}";

        string utilStr = (latestUtilization * 100f).ToString("F0");
        return $"{displayName}\n{typeLine}\n{utilStr}%  Q:{latestQueue}{machineInfo}";
    }

    private void LateUpdate()
    {
        if (labelTMP == null)
        {
            return;
        }

        Camera referenceCamera = Camera.main;
        if (referenceCamera == null)
        {
            Camera[] cameras = Camera.allCameras;
            for (int i = 0; i < cameras.Length; i++)
            {
                if (cameras[i] != null && cameras[i].isActiveAndEnabled)
                {
                    referenceCamera = cameras[i];
                    break;
                }
            }
        }

        if (referenceCamera == null)
        {
            return;
        }

        Vector3 directionToCamera = labelTMP.transform.position - referenceCamera.transform.position;
        if (directionToCamera.sqrMagnitude > 0.001f)
        {
            labelTMP.transform.rotation = Quaternion.LookRotation(directionToCamera.normalized, Vector3.up);
        }
    }

    private Material ResolveTargetMaterial(float util, int queue, string status, bool isBottleneck)
    {
        string normalizedStatus = (status ?? string.Empty).Trim().ToLowerInvariant();

        if (normalizedStatus == "broken")
        {
            return FirstNonNull(matGray, legacyBrokenMat);
        }

        if (isBottleneck || util >= CriticalUtilizationThreshold || queue >= 3)
        {
            return FirstNonNull(matRed, matOrange, legacyMaintenanceMat, legacyRunningMat);
        }

        if (util >= HighUtilizationThreshold || queue >= 2)
        {
            return FirstNonNull(matOrange, legacyMaintenanceMat, matAmber, legacyIdleMat, legacyRunningMat);
        }

        if (util >= MediumUtilizationThreshold || queue >= 1 || normalizedStatus == "running")
        {
            return FirstNonNull(matAmber, legacyIdleMat, legacyMaintenanceMat, legacyRunningMat);
        }

        return FirstNonNull(matGreen, legacyRunningMat, legacyIdleMat);
    }

    private static Material FirstNonNull(params Material[] materials)
    {
        foreach (Material material in materials)
        {
            if (material != null)
            {
                return material;
            }
        }

        return null;
    }

    private static Color ResolveStatusColor(float util, int queue, string status, bool isBottleneck, Material targetMat)
    {
        if (targetMat != null)
        {
            return targetMat.color;
        }

        string normalizedStatus = (status ?? string.Empty).Trim().ToLowerInvariant();
        if (normalizedStatus == "broken")
        {
            return new Color(0.45f, 0.45f, 0.45f, 1f);
        }

        if (isBottleneck || util >= CriticalUtilizationThreshold || queue >= 3)
        {
            return new Color(0.85f, 0.2f, 0.2f, 1f);
        }

        if (util >= HighUtilizationThreshold || queue >= 2)
        {
            return new Color(1f, 0.55f, 0.1f, 1f);
        }

        if (util >= MediumUtilizationThreshold || queue >= 1 || normalizedStatus == "running")
        {
            return new Color(1f, 0.84f, 0.2f, 1f);
        }

        return new Color(0.2f, 0.75f, 0.3f, 1f);
    }

    private IEnumerator PulseArrow()
    {
        // Keep this as requested/existing
        while (isActiveAndEnabled)
        {
            float duration = 0.8f;
            float elapsed = 0f;
            while (elapsed < duration / 2f)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / (duration / 2f);
                float scale = Mathf.SmoothStep(1.0f, 1.5f, t);
                bottleneckArrow.transform.localScale = new Vector3(scale, scale, scale);
                yield return null;
            }
            elapsed = 0f;
            while (elapsed < duration / 2f)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / (duration / 2f);
                float scale = Mathf.SmoothStep(1.5f, 1.0f, t);
                bottleneckArrow.transform.localScale = new Vector3(scale, scale, scale);
                yield return null;
            }
        }
    }

    void ApplyColorToAllRenderers(Color color)
    {
        if (cachedRenderers == null || cachedRenderers.Length == 0) CacheRenderers();
        
        MaterialPropertyBlock mpb = new MaterialPropertyBlock();
        mpb.SetColor("_BaseColor", color); // URP
        mpb.SetColor("_Color", color);     // Standard

        foreach (var r in cachedRenderers)
        {
            if (r == null) continue;
            string n = r.gameObject.name.ToLower();
            // Skip UI/label/arrow/floor objects
            if (n.Contains("label") || n.Contains("text") ||
                n.Contains("canvas") || n.Contains("arrow") ||
                n.Contains("floor")  || n.Contains("queue")) continue;

            r.SetPropertyBlock(mpb);
        }
    }

    System.Collections.IEnumerator PulseColor(Color bright, Color dim)
    {
        while (true)
        {
            ApplyColorToAllRenderers(bright);
            yield return new WaitForSeconds(0.4f);
            ApplyColorToAllRenderers(dim);
            yield return new WaitForSeconds(0.4f);
        }
    }
}
