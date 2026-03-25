using UnityEngine;

/// <summary>
/// Diagnostic tool to check MachineSpawner configuration
/// Add this to an empty GameObject in your scene
/// </summary>
public class SpawnDiagnostic : MonoBehaviour
{
    [Header("References")]
    public MachineSpawner spawner;
    public SimulationManager simManager;
    public Transform factoryParent;
    
    [Header("Diagnostics")]
    public bool runOnStart = true;
    public bool showGUI = true;
    
    [Header("Test Spawn")]
    public bool testSpawn = false;
    public GameObject testPrefab;
    
    private string diagnosticResult = "";
    private bool allChecksPassed = false;
    
    void Awake()
    {
        if (spawner == null)
            spawner = FindFirstObjectByType<MachineSpawner>();

        if (simManager == null)
            simManager = FindFirstObjectByType<SimulationManager>();

        if (factoryParent == null)
            factoryParent = FindFirstObjectByType<Transform>();
    }
    
    void Start()
    {
        if (runOnStart)
            RunDiagnostics();
    }
    
    void Update()
    {
        if (testSpawn && testPrefab != null)
        {
            testSpawn = false;
            PerformTestSpawn();
        }
    }
    
    [ContextMenu("Run Diagnostics")]
    public void RunDiagnostics()
    {
        diagnosticResult = "";
        allChecksPassed = true;
        
        Log("═══════════════════════════════════════════");
        Log("MACHINE SPAWNER DIAGNOSTIC TOOL");
        Log("═══════════════════════════════════════════");
        
        // Check 1: MachineSpawner exists
        if (spawner == null)
        {
            LogError("❌ MachineSpawner not found in scene!");
            allChecksPassed = false;
        }
        else
        {
            Log("✅ MachineSpawner found");
            
            // Check 2: Config path
            string configPath = spawner.configPath;
            Log($"Config Path: {configPath}");
            
            string fullPath = System.IO.Path.Combine(Application.dataPath + "/..", configPath);
            if (System.IO.File.Exists(fullPath))
            {
                Log($"✅ Config file exists at: {fullPath}");
                string content = System.IO.File.ReadAllText(fullPath);
                Log($"Config file size: {content.Length} chars");
                
                // Check for lathe in config
                if (content.Contains("\"icon\": \"lathe\""))
                {
                    Log("✅ Config contains lathe stations");
                }
                else
                {
                    LogError("❌ Config does NOT contain lathe stations!");
                }
            }
            else
            {
                LogError($"❌ Config file NOT FOUND at: {fullPath}");
                allChecksPassed = false;
            }
            
            // Check 3: Prefabs assigned
            Log("───────────────────────────────────────────");
            Log("PREFAB ASSIGNMENTS:");
            
            CheckPrefab("Lathe Prefab", spawner.lathePrefab);
            CheckPrefab("Cnc Prefab", spawner.cncPrefab);
            CheckPrefab("Band Saw Prefab", spawner.bandSawPrefab);
            CheckPrefab("Floor Prefab", spawner.floorPrefab);
            
            // Check 4: Factory Parent
            Log("───────────────────────────────────────────");
            if (spawner.factoryParent == null)
            {
                LogError("❌ Factory Parent NOT assigned!");
                allChecksPassed = false;
            }
            else
            {
                Log($"✅ Factory Parent assigned: {spawner.factoryParent.name}");
            }
            
            // Check 5: Simulation Manager
            if (spawner.simManager == null)
            {
                LogError("❌ Simulation Manager NOT assigned!");
                allChecksPassed = false;
            }
            else
            {
                Log($"✅ Simulation Manager assigned: {spawner.simManager.name}");
            }
            
            // Check 6: MachineVisual on lathe prefab
            Log("───────────────────────────────────────────");
            if (spawner.lathePrefab != null)
            {
                MachineVisual mv = spawner.lathePrefab.GetComponent<MachineVisual>();
                if (mv == null)
                {
                    mv = spawner.lathePrefab.GetComponentInChildren<MachineVisual>();
                }
                
                if (mv == null)
                {
                    LogError("❌ MachineVisual NOT found on lathe prefab!");
                    Log("   Please add MachineVisual component to lathe.prefab");
                    allChecksPassed = false;
                }
                else
                {
                    Log("✅ MachineVisual found on lathe prefab");
                    
                    // Check materials
                    if (mv.matGreen == null) Log("⚠️  Mat Green not assigned");
                    if (mv.matAmber == null) Log("⚠️  Mat Amber not assigned");
                    if (mv.matOrange == null) Log("⚠️  Mat Orange not assigned");
                    if (mv.matRed == null) Log("⚠️  Mat Red not assigned");
                    if (mv.matGray == null) Log("⚠️  Mat Gray not assigned");
                    
                    bool allMatsAssigned = mv.matGreen != null && mv.matAmber != null && 
                                          mv.matOrange != null && mv.matRed != null && 
                                          mv.matGray != null;
                    
                    if (allMatsAssigned)
                        Log("✅ All materials assigned");
                }
            }
        }
        
        // Check 7: Simulation Manager WebSocket
        Log("───────────────────────────────────────────");
        if (simManager != null)
        {
            Log($"WebSocket URL: {simManager.WebSocketUrl}");
            Log($"Auto Connect: {simManager.autoConnect}");
        }
        else
        {
            LogError("❌ SimulationManager not found!");
        }
        
        Log("═══════════════════════════════════════════");
        
        if (allChecksPassed)
        {
            Log("✅ ALL CHECKS PASSED - Ready to spawn!");
        }
        else
        {
            Log("❌ SOME CHECKS FAILED - Fix issues above");
        }
        
        Log("═══════════════════════════════════════════");
    }
    
    void CheckPrefab(string name, GameObject prefab)
    {
        if (prefab == null)
        {
            LogError($"❌ {name}: NOT ASSIGNED");
        }
        else
        {
            Log($"✅ {name}: {prefab.name}");
        }
    }
    
    [ContextMenu("Test Spawn Lathe")]
    public void PerformTestSpawn()
    {
        Log("───────────────────────────────────────────");
        Log("PERFORMING TEST SPAWN...");
        
        if (spawner == null || spawner.lathePrefab == null)
        {
            LogError("❌ Cannot test spawn - lathe prefab not assigned");
            return;
        }
        
        if (factoryParent == null)
        {
            LogError("❌ Cannot test spawn - factory parent not assigned");
            return;
        }
        
        // Spawn test lathe
        GameObject testLathe = Instantiate(spawner.lathePrefab, factoryParent);
        testLathe.name = "TEST_LATHE_DEBUG";
        testLathe.transform.localPosition = Vector3.zero;
        
        Log($"✅ Test lathe spawned: {testLathe.name}");
        Log($"   Position: {testLathe.transform.localPosition}");
        Log($"   Parent: {testLathe.transform.parent?.name}");
        
        // Check if it has MachineVisual
        MachineVisual mv = testLathe.GetComponent<MachineVisual>();
        if (mv == null)
        {
            mv = testLathe.GetComponentInChildren<MachineVisual>();
        }
        
        if (mv != null)
        {
            Log("✅ MachineVisual component found");
            mv.UpdateStatus(0.5f, 2, "running", false);
            Log("   Updated status: 50% util, queue=2");
        }
        else
        {
            LogError("❌ MachineVisual NOT found on spawned lathe!");
        }
    }
    
    void Log(string message)
    {
        Debug.Log($"[DIAGNOSTIC] {message}");
        diagnosticResult += message + "\n";
    }
    
    void LogError(string message)
    {
        Debug.LogError($"[DIAGNOSTIC] {message}");
        diagnosticResult += message + "\n";
    }
    
    void OnGUI()
    {
        if (!showGUI) return;
        
        GUI.Box(new Rect(10, 10, 400, 500), "Machine Spawner Diagnostic");
        
        GUILayout.BeginArea(new Rect(20, 40, 380, 460));
        
        GUILayout.BeginVertical();
        
        GUILayout.Label("Status: " + (allChecksPassed ? "✅ PASS" : "❌ FAIL"));
        GUILayout.Space(10);
        
        // Scrollable text area
        GUILayout.BeginVertical(GUI.skin.box);
        GUILayout.Label(diagnosticResult);
        GUILayout.EndVertical();
        
        GUILayout.Space(10);
        
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Run Diagnostics"))
        {
            RunDiagnostics();
        }
        
        if (GUILayout.Button("Test Spawn"))
        {
            testSpawn = true;
        }
        GUILayout.EndHorizontal();
        
        GUILayout.EndVertical();
        GUILayout.EndArea();
    }
}
