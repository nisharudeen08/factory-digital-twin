using NUnit.Framework;
using UnityEngine;

public class MachineSpawnerEditModeTests
{
    private GameObject simulationManagerObject;
    private GameObject spawnerObject;
    private GameObject factoryParentObject;
    private GameObject prefabObject;

    [SetUp]
    public void SetUp()
    {
        simulationManagerObject = new GameObject("SimulationManager");
        simulationManagerObject.AddComponent<SimulationManager>();

        spawnerObject = new GameObject("MachineSpawner");
        factoryParentObject = new GameObject("FactoryParent");
    }

    [TearDown]
    public void TearDown()
    {
        if (factoryParentObject != null)
        {
            Object.DestroyImmediate(factoryParentObject);
        }

        if (spawnerObject != null)
        {
            Object.DestroyImmediate(spawnerObject);
        }

        if (simulationManagerObject != null)
        {
            Object.DestroyImmediate(simulationManagerObject);
        }

        if (prefabObject != null)
        {
            Object.DestroyImmediate(prefabObject);
        }
    }

    [Test]
    public void SpawnFromJson_CreatesConfiguredMachineInstances()
    {
        MachineSpawner spawner = spawnerObject.AddComponent<MachineSpawner>();
        spawner.factoryParent = factoryParentObject.transform;
        prefabObject = CreateMachinePrefab();
        spawner.grindingPrefab = prefabObject;
        spawner.lathePrefab = prefabObject;

        string json = "{\"stations\":[{\"id\":7,\"name\":\"Lathe\",\"icon\":\"lathe\",\"num_machines\":2,\"position_x\":4.0,\"position_z\":6.0}]}";

        spawner.BuildFactory(json);

        Assert.That(factoryParentObject.transform.childCount, Is.EqualTo(2));

        MachineVisual[] visuals = factoryParentObject.GetComponentsInChildren<MachineVisual>();
        Assert.That(visuals.Length, Is.EqualTo(2));
        Assert.That(visuals[0].stationId, Is.EqualTo(7));
        Assert.That(visuals[1].stationId, Is.EqualTo(7));
        Assert.That(factoryParentObject.transform.GetChild(0).name, Does.StartWith("S7_M1_lathe"));
        Assert.That(factoryParentObject.transform.GetChild(1).name, Does.StartWith("S7_M2_lathe"));
    }

    private static GameObject CreateMachinePrefab()
    {
        GameObject prefab = new GameObject("MachinePrefab");
        prefab.AddComponent<MeshRenderer>();
        prefab.AddComponent<MeshFilter>();
        prefab.AddComponent<MachineVisual>();
        return prefab;
    }
}