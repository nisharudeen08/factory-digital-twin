using UnityEngine;

public class FloorManager : MonoBehaviour
{
    [Header("Assign in Inspector")]
    public GameObject floorObject;      // your floor plane/cube
    public Transform  factoryParent;    // same as MachineSpawner

    [Header("Floor Settings")]
    public float minFloorSize  = 10f;   // minimum floor size
    public float machineSpacing = 5f;   // gap between stations
    public float floorMargin   = 4f;    // extra border around machines

    [Header("Floor Material (optional)")]
    public Material floorMaterial;

    // Called by MachineSpawner after BuildFactory()
    public void ResizeFloor(int stationCount, int totalMachines)
    {
        if (floorObject == null) {
            Debug.LogWarning("[Floor] No floor object assigned!");
            return;
        }

        // Calculate floor size based on machines
        float width = CalculateWidth(stationCount);
        float depth = CalculateDepth(totalMachines);

        // Apply to floor object
        // Unity plane default is 10x10 units. Verify if it's a Plane or Cube.
        bool isPlane = floorObject.name.ToLower().Contains("plane") || 
                       floorObject.name.ToLower().Contains("floor");

        if (isPlane) {
            floorObject.transform.localScale = new Vector3(width / 10f, 1f, depth / 10f);
        } else {
            floorObject.transform.localScale = new Vector3(width, 0.1f, depth);
        }

        // Center floor under factory (accounting for parent offset)
        Vector3 parentPos = factoryParent != null ? factoryParent.position : Vector3.zero;
        float centerX = (stationCount - 1) * machineSpacing / 2f;
        
        floorObject.transform.position = parentPos + new Vector3(
            centerX,
            -0.05f,  // just below machines
            0f
        );

        Debug.Log($"[Floor] Resized to {width:F1}m × {depth:F1}m");
    }

    private float CalculateWidth(int stationCount)
    {
        // Width = number of stations × spacing + margin on both sides
        float calculated = (stationCount * machineSpacing) + floorMargin * 2f;
        return Mathf.Max(calculated, minFloorSize);
    }

    private float CalculateDepth(int totalMachines)
    {
        // Depth grows with parallel machines per station
        // Base depth = 8m, grows by 2m per extra machine layer
        float calculated = 8f + (totalMachines * 0.4f) + floorMargin;
        return Mathf.Max(calculated, minFloorSize);
    }

    // Auto-generate a grid pattern on the floor
    public void DrawFloorGrid(int stationCount, int totalMachines)
    {
        if (floorMaterial == null) return;

        float width = CalculateWidth(stationCount);
        float depth = CalculateDepth(totalMachines);

        // Set tiling based on floor size
        floorMaterial.mainTextureScale =
            new Vector2(width / 2f, depth / 2f);
    }
}
