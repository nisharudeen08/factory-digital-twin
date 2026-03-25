using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class CameraUI : MonoBehaviour
{
    [Header("References")]
    [SerializeField]
    private CameraController cameraController;

    [SerializeField]
    private CinematicCamera cinematicCamera;

    [SerializeField]
    private Button cinematicButton;

    [SerializeField]
    private TextMeshProUGUI cinematicBtnText;

    private bool cinematicActive = false;

    public void OnReset()
    {
        if (cameraController != null)
            cameraController.FocusOnFactory();
    }

    public void OnBack()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        try
        {
            using (var unityPlayer =
                new AndroidJavaClass(
                    "com.unity3d.player" +
                    ".UnityPlayer"))
            using (var activity =
                unityPlayer.GetStatic
                    <AndroidJavaObject>(
                    "currentActivity"))
            {
                activity.Call("finish");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError(
                "[CameraUI] Back error: "
                + e.Message);
        }
#else
        Debug.Log(
            "[CameraUI] Back (Editor mode)");
#endif
    }

    public void OnCinematic()
    {
        if (cinematicCamera == null)
        {
            Debug.LogError(
                "[CameraUI] cinematicCamera" +
                " is NULL. Wire it in Inspector.");
            return;
        }

        if (cameraController == null)
        {
            Debug.LogError(
                "[CameraUI] cameraController" +
                " is NULL. Wire it in Inspector.");
            return;
        }

        cinematicActive = !cinematicActive;

        if (cinematicActive)
        {
            cinematicCamera.StartCinematic();
            if (cinematicBtnText != null)
                cinematicBtnText.text = "STOP";
            Debug.Log(
                "[CameraUI] Cinematic ON");
        }
        else
        {
            cinematicCamera.StopCinematic();
            if (cinematicBtnText != null)
                cinematicBtnText.text =
                    "CINEMATIC";
            Debug.Log(
                "[CameraUI] Cinematic OFF");
        }
    }
}
