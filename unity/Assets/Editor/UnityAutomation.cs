using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using System.IO;

public class UnityAutomation
{
    [MenuItem("Automation/Prepare Android Export")]
    public static void PrepareAndroidExport()
    {
        string scenePath = "Assets/Scenes/factory_digital twin.unity";
        var scene = EditorSceneManager.OpenScene(scenePath);
        
        MachineSpawner[] spawners = GameObject.FindObjectsByType<MachineSpawner>(FindObjectsSortMode.None);
        Debug.Log($"[Automation] Found {spawners.Length} MachineSpawners.");

        foreach (var spawner in spawners)
        {
            // Step 1 check: Null prefabs
            // The instructions say "Delete the one with NULL prefabs. Keep only the one with lathe Variant Variant."
            bool hasLathe = (spawner.lathePrefab != null);
            
            if (!hasLathe)
            {
                Debug.Log($"[Automation] Deleting spawner on '{spawner.gameObject.name}' because lathePrefab is NULL.");
                Undo.DestroyObjectImmediate(spawner.gameObject);
            }
            else
            {
                Debug.Log($"[Automation] Keeping spawner on '{spawner.gameObject.name}'.");
                // Step 2: Clear configPath
                spawner.configPath = "";
                EditorUtility.SetDirty(spawner);
                Debug.Log($"[Automation] Cleared configPath on '{spawner.gameObject.name}'.");
            }
        }

        EditorSceneManager.SaveScene(scene);
        Debug.Log("[Automation] Scene saved.");

        // Step 3: Export to Android
        ExportToAndroid();
    }

    public static void ExportToAndroid()
    {
        Debug.Log("[Automation] Starting Android Export...");
        
        string[] scenes = { "Assets/Scenes/factory_digital twin.unity" };
        string exportPath = Path.Combine(Directory.GetCurrentDirectory(), "..", "unityExport");
        
        // Ensure export path exists
        if (!Directory.Exists(exportPath)) Directory.CreateDirectory(exportPath);

        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.scenes = scenes;
        buildPlayerOptions.locationPathName = exportPath;
        buildPlayerOptions.target = BuildTarget.Android;
        buildPlayerOptions.options = BuildOptions.AcceptExternalModificationsToPlayer; // This corresponds to "Export Project"

        BuildPipeline.BuildPlayer(buildPlayerOptions);
        Debug.Log("[Automation] Android Export completed to: " + exportPath);
    }
}
