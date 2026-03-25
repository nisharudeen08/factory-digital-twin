using System;
using System.Collections;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class FactoryScenePlayModeTests
{
    private const string SceneName = "factory";
    private const int TestStationId = 9001;
    private const string SimulationManagerTypeName = "SimulationManager";
    private const string MachineSpawnerTypeName = "MachineSpawner";
    private const string MachineVisualTypeName = "MachineVisual";

    [UnitySetUp]
    public IEnumerator SetUp()
    {
        SetSimulationManagerTestAutoConnectSuppression(true);
        SceneManager.LoadScene(SceneName, LoadSceneMode.Single);
        yield return null;
        yield return null;
    }

    [UnityTearDown]
    public IEnumerator TearDown()
    {
        SetSimulationManagerTestAutoConnectSuppression(false);
        yield return null;
    }

    [UnityTest]
    public IEnumerator FactoryScene_CanSpawnConfiguredMachinesInPlayMode()
    {
        Type simulationManagerType = FindType(SimulationManagerTypeName);
        Type machineSpawnerType = FindType(MachineSpawnerTypeName);
        Type machineVisualType = FindType(MachineVisualTypeName);
        MonoBehaviour simulationManager = FindBehaviour(simulationManagerType);
        MonoBehaviour spawner = FindBehaviour(machineSpawnerType);

        Assert.That(simulationManager, Is.Not.Null);
        Assert.That(spawner, Is.Not.Null);
        Assert.That(GetStaticPropertyValue(simulationManagerType, "Instance"), Is.SameAs(simulationManager));
        Assert.That(GetFieldValue<Transform>(spawner, "factoryParent"), Is.Not.Null);
        Assert.That(GetFieldValue<GameObject>(spawner, "genericMachinePrefab"), Is.Not.Null);

        string json = "{\"stations\":[{\"id\":9001,\"name\":\"PlayModeLathe\",\"icon\":\"unknown\",\"numMachines\":2,\"positionX\":4,\"positionZ\":6}]}";

        InvokeMethod(spawner, "SpawnFromJSON", json);
        yield return null;
        yield return null;

        int matchingVisuals = 0;
        MonoBehaviour[] allBehaviours = UnityEngine.Object.FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None);
        foreach (MonoBehaviour behaviour in allBehaviours)
        {
            if (behaviour == null || behaviour.GetType() != machineVisualType)
            {
                continue;
            }

            if (GetFieldValue<int>(behaviour, "stationId") == TestStationId)
            {
                matchingVisuals++;
            }
        }

        Assert.That(GetFieldValue<Transform>(spawner, "factoryParent").childCount, Is.EqualTo(2));
        Assert.That(matchingVisuals, Is.EqualTo(2));
    }

    private static void SetSimulationManagerTestAutoConnectSuppression(bool value)
    {
        Type simulationManagerType = FindType(SimulationManagerTypeName);
        PropertyInfo property = simulationManagerType.GetProperty(
            "SuppressAutoConnectForTests",
            BindingFlags.Public | BindingFlags.Static);

        Assert.That(property, Is.Not.Null, "SimulationManager.SuppressAutoConnectForTests was not found.");
        property.SetValue(null, value);
    }

    private static Type FindType(string typeName)
    {
        foreach (Assembly assembly in System.AppDomain.CurrentDomain.GetAssemblies())
        {
            Type type = assembly.GetType(typeName);
            if (type != null)
            {
                return type;
            }
        }

        Assert.Fail($"Type '{typeName}' was not found in loaded assemblies.");
        return null;
    }

    private static MonoBehaviour FindBehaviour(Type targetType)
    {
        MonoBehaviour[] behaviours = UnityEngine.Object.FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None);
        foreach (MonoBehaviour behaviour in behaviours)
        {
            if (behaviour != null && behaviour.GetType() == targetType)
            {
                return behaviour;
            }
        }

        return null;
    }

    private static object GetStaticPropertyValue(Type type, string propertyName)
    {
        PropertyInfo property = type.GetProperty(propertyName, BindingFlags.Public | BindingFlags.Static);
        Assert.That(property, Is.Not.Null, $"Static property '{propertyName}' was not found on '{type.Name}'.");
        return property.GetValue(null);
    }

    private static T GetFieldValue<T>(object instance, string fieldName)
    {
        FieldInfo field = instance.GetType().GetField(fieldName, BindingFlags.Public | BindingFlags.Instance);
        Assert.That(field, Is.Not.Null, $"Field '{fieldName}' was not found on '{instance.GetType().Name}'.");
        return (T)field.GetValue(instance);
    }

    private static void InvokeMethod(object instance, string methodName, params object[] arguments)
    {
        MethodInfo method = instance.GetType().GetMethod(methodName, BindingFlags.Public | BindingFlags.Instance);
        Assert.That(method, Is.Not.Null, $"Method '{methodName}' was not found on '{instance.GetType().Name}'.");
        method.Invoke(instance, arguments);
    }
}
