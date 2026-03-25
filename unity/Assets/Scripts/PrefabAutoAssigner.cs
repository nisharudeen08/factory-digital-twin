using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

/// <summary>
/// Quick fix script to verify and auto-assign prefabs
/// Add this to GameManager alongside MachineSpawner
/// </summary>
public class PrefabAutoAssigner : MonoBehaviour
{
    [Header("Auto-Assign Settings")]
    public bool autoAssignOnStart = true;
    public MachineSpawner spawner;

    [Header("Prefab Search Paths")]
    public string prefabFolder = "Assets/prefab/";

    [Header("Debug")]
    public bool forceReassign = false;

    void Start()
    {
        if (autoAssignOnStart)
        {
            Invoke(nameof(CheckAndAssignPrefabs), 0.5f);
        }
    }

    [ContextMenu("Check and Assign Prefabs")]
    public void CheckAndAssignPrefabs()
    {
        if (spawner == null)
        {
            spawner = GetComponent<MachineSpawner>();
        }

        if (spawner == null)
        {
            Debug.LogError("[PrefabAutoAssigner] No MachineSpawner found!");
            return;
        }

        Debug.Log("[PrefabAutoAssigner] Checking prefab assignments...");

        // Check each prefab slot - use exact names
        if (spawner.lathePrefab == null || forceReassign)
        {
            spawner.lathePrefab = FindPrefabExact("lathe");
            Debug.Log(spawner.lathePrefab != null
                ? "[PrefabAutoAssigner] ✅ Auto-assigned lathe prefab"
                : "[PrefabAutoAssigner] ❌ Could not find lathe prefab");
        }

        if (spawner.cncPrefab == null || forceReassign)
        {
            spawner.cncPrefab = FindPrefabExact("milling");
            Debug.Log(spawner.cncPrefab != null
                ? "[PrefabAutoAssigner] ✅ Auto-assigned cnc/milling prefab"
                : "[PrefabAutoAssigner] ❌ Could not find cnc/milling prefab");
        }

        if (spawner.bandSawPrefab == null || forceReassign)
        {
            spawner.bandSawPrefab = FindPrefabExact("band_saw");
            Debug.Log(spawner.bandSawPrefab != null
                ? "[PrefabAutoAssigner] ✅ Auto-assigned band_saw prefab"
                : "[PrefabAutoAssigner] ❌ Could not find band_saw prefab");
        }

        if (spawner.floorPrefab == null || forceReassign)
        {
            spawner.floorPrefab = FindPrefabExact("floor");
            Debug.Log(spawner.floorPrefab != null
                ? "[PrefabAutoAssigner] ✅ Auto-assigned floor prefab"
                : "[PrefabAutoAssigner] ❌ Could not find floor prefab");
        }

        if (spawner.grindingPrefab == null || forceReassign)
        {
            // Use grinding as generic fallback
            spawner.grindingPrefab = FindPrefabExact("grinding1");
            Debug.Log(spawner.grindingPrefab != null
                ? "[PrefabAutoAssigner] ✅ Auto-assigned grinding prefab (grinding1)"
                : "[PrefabAutoAssigner] ❌ Could not find grinding prefab");
        }

        // Assign missing station prefabs to lathe as temporary
        if (spawner.drillPrefab == null || forceReassign)
        {
            spawner.drillPrefab = spawner.lathePrefab;
            Debug.Log("[PrefabAutoAssigner] ⚠️  Using lathe for drill (temporary)");
        }

        if (spawner.weldPrefab == null || forceReassign)
        {
            spawner.weldPrefab = spawner.lathePrefab;
            Debug.Log("[PrefabAutoAssigner] ⚠️  Using lathe for weld (temporary)");
        }

        Debug.Log("[PrefabAutoAssigner] Prefab check complete!");
        Debug.Log($"[PrefabAutoAssigner] Lathe: {(spawner.lathePrefab != null ? "✅" : "❌")}");
        Debug.Log($"[PrefabAutoAssigner] CNC: {(spawner.cncPrefab != null ? "✅" : "❌")}");
        Debug.Log($"[PrefabAutoAssigner] Band Saw: {(spawner.bandSawPrefab != null ? "✅" : "❌")}");
        Debug.Log($"[PrefabAutoAssigner] Floor: {(spawner.floorPrefab != null ? "✅" : "❌")}");
        Debug.Log($"[PrefabAutoAssigner] Grinding: {(spawner.grindingPrefab != null ? "✅" : "❌")}");
        
        if (forceReassign)
        {
            forceReassign = false;
            Debug.Log("[PrefabAutoAssigner] Force reassign complete. Uncheck forceReassign to prevent overwriting.");
        }
    }

    GameObject FindPrefabExact(string name)
    {
        GameObject prefab = null;

#if UNITY_EDITOR
        // Try direct path first - exact match
        string path = prefabFolder + name + ".prefab";
        prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (prefab != null)
        {
            Debug.Log($"[PrefabAutoAssigner] Found {name} at {path}");
            return prefab;
        }
#endif

        // Try to find in Resources
        prefab = Resources.Load<GameObject>(name);
        if (prefab != null)
        {
            Debug.Log($"[PrefabAutoAssigner] Found {name} in Resources");
            return prefab;
        }

#if UNITY_EDITOR
        // Search all assets for exact name match
        string[] guids = AssetDatabase.FindAssets(name + " t:prefab");
        if (guids.Length > 0)
        {
            // First try exact match
            foreach (var g in guids)
            {
                string p = AssetDatabase.GUIDToAssetPath(g);
                string fileName = System.IO.Path.GetFileNameWithoutExtension(p);
                if (fileName.ToLower() == name.ToLower())
                {
                    prefab = AssetDatabase.LoadAssetAtPath<GameObject>(p);
                    if (prefab != null)
                    {
                        Debug.Log($"[PrefabAutoAssigner] Found exact match {name} at {p}");
                        return prefab;
                    }
                }
            }
            
            // Fallback to first match containing the name (excluding Variants)
            foreach (var g in guids)
            {
                string p = AssetDatabase.GUIDToAssetPath(g);
                string fileName = System.IO.Path.GetFileNameWithoutExtension(p);
                if (fileName.ToLower().Contains(name.ToLower()) && !fileName.Contains("Variant"))
                {
                    prefab = AssetDatabase.LoadAssetAtPath<GameObject>(p);
                    if (prefab != null)
                    {
                        Debug.Log($"[PrefabAutoAssigner] Found {name} at {p}");
                        return prefab;
                    }
                }
            }
        }
#endif

        Debug.LogWarning($"[PrefabAutoAssigner] Could not find prefab: {name}");
        return null;
    }
}

