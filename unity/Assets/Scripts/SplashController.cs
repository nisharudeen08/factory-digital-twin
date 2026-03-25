using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using UnityEngine.SceneManagement;

public class SplashController : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private TextMeshProUGUI companyText;
    [SerializeField] private TextMeshProUGUI productText;
    [SerializeField] private Image backgroundPanel;

    [Header("Timing")]
    [SerializeField] private float holdSeconds    = 1.8f;
    [SerializeField] private float fadeInSeconds  = 0.6f;
    [SerializeField] private float fadeOutSeconds = 0.5f;

    void Start()
    {
        // Set text content in code
        // so it works even if Inspector is not wired
        if (companyText  != null)
            companyText.text  = "Made by Lumis";
        if (productText  != null)
            productText.text  = "Factory Digital Twin";

        // Start fully transparent
        SetAlpha(0f);

        StartCoroutine(SplashSequence());
    }

    private IEnumerator SplashSequence()
    {
        // Fade in
        float t = 0f;
        while (t < fadeInSeconds)
        {
            t += Time.deltaTime;
            SetAlpha(Mathf.Clamp01(t / fadeInSeconds));
            yield return null;
        }
        SetAlpha(1f);

        // Hold
        yield return new WaitForSeconds(holdSeconds);

        // Fade out
        t = 0f;
        while (t < fadeOutSeconds)
        {
            t += Time.deltaTime;
            SetAlpha(1f - Mathf.Clamp01(
                t / fadeOutSeconds));
            yield return null;
        }
        SetAlpha(0f);

        // Load main scene
        SceneManager.LoadScene(1);
    }

    private void SetAlpha(float alpha)
    {
        if (companyText != null)
        {
            Color c = companyText.color;
            c.a = alpha;
            companyText.color = c;
        }
        if (productText != null)
        {
            Color c = productText.color;
            c.a = alpha;
            productText.color = c;
        }
    }
}
