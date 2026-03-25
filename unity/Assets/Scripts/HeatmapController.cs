using UnityEngine;

public class HeatmapController : MonoBehaviour
{
    [Header("Heatmap Setup")]
    public Renderer floorRenderer;
    public Color lowUtilizationColor = new Color(0.2f, 0.8f, 0.2f, 0.5f);  // Transparent Green
    public Color highUtilizationColor = new Color(0.8f, 0.2f, 0.2f, 0.5f); // Transparent Red
    
    // We assume the floor has a material that supports proper tinting (e.g. Standard, Transparent)
    
    private float targetIntensity = 0f;
    private float currentIntensity = 0f;

    void Update()
    {
        // Smooth transition for heatmap color changes
        if (Mathf.Abs(currentIntensity - targetIntensity) > 0.01f)
        {
            currentIntensity = Mathf.Lerp(currentIntensity, targetIntensity, Time.deltaTime * 2f);
            
            if (floorRenderer != null && floorRenderer.material != null)
            {
                Color lerpedColor = Color.Lerp(lowUtilizationColor, highUtilizationColor, currentIntensity);
                floorRenderer.material.color = lerpedColor;
            }
        }
    }

    // Called by SimulationManager based on average or max util
    public void SetHeatmapIntensity(float maxUtilization)
    {
        // maxUtilization should be between 0.0 and 1.0
        targetIntensity = Mathf.Clamp01(maxUtilization);
    }
}
