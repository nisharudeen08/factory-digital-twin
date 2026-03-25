using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class FactorySetupEditor
{
    [MenuItem("Factory/Setup Scene")]
    public static void SetupFactoryScene()
    {
        // Factory parent
        GameObject factoryParent = GameObject.Find("FactoryParent");
        if (factoryParent == null) factoryParent = new GameObject("FactoryParent");

        // SimulationManager
        GameObject simGO = GameObject.Find("SimulationManager");
        if (simGO == null) simGO = new GameObject("SimulationManager");
        var sim = simGO.GetComponent<SimulationManager>() ?? simGO.AddComponent<SimulationManager>();

        // MachineSpawner
        GameObject spawnerGO = GameObject.Find("MachineSpawner");
        if (spawnerGO == null) spawnerGO = new GameObject("MachineSpawner");
        var spawner = spawnerGO.GetComponent<MachineSpawner>() ?? spawnerGO.AddComponent<MachineSpawner>();
        spawner.factoryParent = factoryParent.transform;
        spawner.simManager = sim;

        // Try to assign common prefabs by name (searches the project)
        spawner.lathePrefab     = spawner.lathePrefab     ?? LoadPrefabByName("lathe");
        spawner.cncPrefab       = spawner.cncPrefab       ?? LoadPrefabByName("milling");
        spawner.drillPrefab     = spawner.drillPrefab     ?? LoadPrefabByName("drill");
        spawner.bandSawPrefab   = spawner.bandSawPrefab   ?? LoadPrefabByName("band_saw");
        spawner.weldPrefab      = spawner.weldPrefab      ?? LoadPrefabByName("weld");
        spawner.grindingPrefab  = spawner.grindingPrefab  ?? LoadPrefabByName("grinding1");
        spawner.floorPrefab     = spawner.floorPrefab     ?? LoadPrefabByName("floor");

        // Floor object (instantiate prefab or create Plane)
        GameObject floor = GameObject.Find("FactoryFloor");
        if (floor == null)
        {
            if (spawner.floorPrefab != null)
            {
                floor = (GameObject)PrefabUtility.InstantiatePrefab(spawner.floorPrefab);
                floor.name = "FactoryFloor";
                floor.transform.SetParent(factoryParent.transform, false);
            }
            else
            {
                floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
                floor.name = "FactoryFloor";
                floor.transform.SetParent(factoryParent.transform, false);
            }
        }

        // FloorManager
        GameObject fmGO = GameObject.Find("FloorManager");
        if (fmGO == null) fmGO = new GameObject("FloorManager");
        var fm = fmGO.GetComponent<FloorManager>() ?? fmGO.AddComponent<FloorManager>();
        fm.floorObject = floor;
        fm.factoryParent = factoryParent.transform;
        if (spawner.floorPrefab != null) fm.floorMaterial = fm.floorMaterial ?? GetMaterialFromPrefab(spawner.floorPrefab);

        // Ensure a Main Camera exists
        if (Camera.main == null)
        {
            GameObject camGO = GameObject.Find("Main Camera");
            if (camGO == null) camGO = new GameObject("Main Camera");
            var cam = camGO.GetComponent<Camera>() ?? camGO.AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.transform.position = new Vector3(0f, 12f, -18f);
            cam.transform.LookAt(factoryParent.transform);
        }

        // Mark scene dirty and prompt save
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        Debug.Log("[FactorySetup] Scene prepared. Review in Hierarchy and save the scene.");
    }

    static GameObject LoadPrefabByName(string shortName)
    {
        if (string.IsNullOrEmpty(shortName)) return null;
        // Search for prefabs by name (case-insensitive)
        string[] guids = AssetDatabase.FindAssets(shortName + " t:prefab");
        if (guids == null || guids.Length == 0) return null;
        // prefer exact name match
        foreach (var g in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(g);
            string name = System.IO.Path.GetFileNameWithoutExtension(path);
            if (name.ToLower().Contains(shortName.ToLower()))
                return AssetDatabase.LoadAssetAtPath<GameObject>(path);
        }
        // fallback to first
        return AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guids[0]));
    }

    static Material GetMaterialFromPrefab(GameObject prefab)
    {
        if (prefab == null) return null;
        var renders = prefab.GetComponentsInChildren<Renderer>(true);
        foreach (var r in renders)
        {
            if (r.sharedMaterial != null) return r.sharedMaterial;
        }
        return null;
    }
}
