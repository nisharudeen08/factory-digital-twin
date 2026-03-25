#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Events;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;

public class CameraUIGenerator : EditorWindow
{
    [MenuItem("Window/Setup Camera UI")]
    public static void GenerateUI()
    {
        // 1. Create Canvas
        GameObject canvasObj = new GameObject("CameraControlCanvas");
        Canvas c = canvasObj.AddComponent<Canvas>();
        c.renderMode = RenderMode.ScreenSpaceOverlay;
        c.sortingOrder = 10;

        CanvasScaler cs = canvasObj.AddComponent<CanvasScaler>();
        cs.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        cs.referenceResolution = new Vector2(1920, 1080);
        cs.matchWidthOrHeight = 0.5f;

        canvasObj.AddComponent<GraphicRaycaster>();

        // 2. Create EventSystem if not present
        if (Object.FindAnyObjectByType<EventSystem>() == null)
        {
            GameObject esObj = new GameObject("EventSystem");
            esObj.AddComponent<EventSystem>();
            esObj.AddComponent<StandaloneInputModule>();
        }

        // 3. Create CameraUIController
        GameObject uiCtrlObj = new GameObject("CameraUIController");
        CameraUI uiScript = uiCtrlObj.AddComponent<CameraUI>();
        CinematicCamera cinematicScript = uiCtrlObj.AddComponent<CinematicCamera>();
        
        CameraController camCtrl = Object.FindAnyObjectByType<CameraController>();
        if (camCtrl != null)
        {
            var serializedUi = new SerializedObject(uiScript);
            serializedUi.FindProperty("cameraController").objectReferenceValue = camCtrl;
            serializedUi.ApplyModifiedProperties();

            var serializedCin = new SerializedObject(cinematicScript);
            serializedCin.FindProperty("camCtrl").objectReferenceValue = camCtrl;
            serializedCin.ApplyModifiedProperties();
        }

        var uiScriptSerialized = new SerializedObject(uiScript);
        uiScriptSerialized.FindProperty("cinematicCamera").objectReferenceValue = cinematicScript;
        uiScriptSerialized.ApplyModifiedProperties();

        // 4. Create Buttons
        CreateButton(canvasObj.transform, "BackButton", "← BACK", new Vector2(80, -60), new Vector2(140, 60), TextAnchor.UpperLeft, new Color32(26, 26, 46, 204), 22, (btn, txt) => {
            UnityEventTools.AddPersistentListener(btn.onClick, uiScript.OnBack);
        });

        CreateButton(canvasObj.transform, "ResetButton", "⟳ RESET", new Vector2(-80, -60), new Vector2(140, 60), TextAnchor.UpperRight, new Color32(26, 46, 26, 204), 22, (btn, txt) => {
            UnityEventTools.AddPersistentListener(btn.onClick, uiScript.OnReset);
        });

        // Cinematic Button
        CreateButton(canvasObj.transform, "CinematicButton", "🎬 CINEMATIC", new Vector2(0, 80), new Vector2(200, 65), TextAnchor.LowerCenter, new Color32(26, 0, 51, 204), 24, (btn, txt) => {
            UnityEventTools.AddPersistentListener(btn.onClick, uiScript.OnCinematic);
            
            var uiSer = new SerializedObject(uiScript);
            uiSer.FindProperty("cinematicButton").objectReferenceValue = btn;
            uiSer.FindProperty("cinematicBtnText").objectReferenceValue = txt;
            uiSer.ApplyModifiedProperties();
        }, true);

        // 5. Joystick Area (New)
        GameObject joystickArea = new GameObject("JoystickArea");
        joystickArea.transform.SetParent(canvasObj.transform, false);
        RectTransform joystickRt = joystickArea.AddComponent<RectTransform>();
        SetAnchor(joystickRt, TextAnchor.LowerLeft);
        joystickRt.anchoredPosition = new Vector2(120, 120);
        joystickRt.sizeDelta = new Vector2(160, 160);

        VirtualJoystick vJoystick = joystickArea.AddComponent<VirtualJoystick>();

        // Background
        GameObject bgObj = new GameObject("JoystickBackground");
        bgObj.transform.SetParent(joystickArea.transform, false);
        Image bgImg = bgObj.AddComponent<Image>();
        bgImg.color = new Color(1, 1, 1, 60f / 255f);
        bgImg.sprite = Resources.GetBuiltinResource<Sprite>("UI/Skin/Knob.psd");
        RectTransform bgRt = bgObj.GetComponent<RectTransform>();
        bgRt.sizeDelta = new Vector2(160, 160);

        // Handle
        GameObject handleObj = new GameObject("JoystickHandle");
        handleObj.transform.SetParent(joystickArea.transform, false);
        Image handleImg = handleObj.AddComponent<Image>();
        handleImg.color = new Color(1, 1, 1, 180f / 255f);
        handleImg.sprite = Resources.GetBuiltinResource<Sprite>("UI/Skin/Knob.psd");
        handleImg.raycastTarget = false;
        RectTransform handleRt = handleObj.GetComponent<RectTransform>();
        handleRt.sizeDelta = new Vector2(65, 65);

        // Wire Joystick
        var vJoySerialized = new SerializedObject(vJoystick);
        vJoySerialized.FindProperty("background").objectReferenceValue = bgRt;
        vJoySerialized.FindProperty("handle").objectReferenceValue = handleRt;
        vJoySerialized.FindProperty("handleRange").floatValue = 50f;
        vJoySerialized.ApplyModifiedProperties();

        // Wire CameraController to Joystick
        if (camCtrl != null)
        {
            var camSer = new SerializedObject(camCtrl);
            camSer.FindProperty("joystick").objectReferenceValue = vJoystick;
            camSer.ApplyModifiedProperties();
        }

        Debug.Log("[CameraUI] UI successfully generated and wired with Joystick!");
        Selection.activeGameObject = canvasObj;
    }

    private static void CreateButton(Transform parent, string name, string label, Vector2 pos, Vector2 size, TextAnchor anchor, Color color, int fontSize, System.Action<Button, TextMeshProUGUI> action, bool useTMPro = false)
    {
        GameObject btnObj = new GameObject(name);
        btnObj.transform.SetParent(parent, false);

        Image img = btnObj.AddComponent<Image>();
        img.color = color;

        Button btn = btnObj.AddComponent<Button>();
        RectTransform rt = btnObj.GetComponent<RectTransform>();
        SetAnchor(rt, anchor);
        rt.anchoredPosition = pos;
        rt.sizeDelta = size;

        GameObject textObj = new GameObject("Text");
        textObj.transform.SetParent(btnObj.transform, false);

        TextMeshProUGUI tmpText = null;
        if (useTMPro)
        {
            tmpText = textObj.AddComponent<TextMeshProUGUI>();
            tmpText.text = label;
            tmpText.fontSize = fontSize;
            tmpText.alignment = TextAlignmentOptions.Center;
            tmpText.color = Color.white;
            tmpText.fontStyle = FontStyles.Bold;
        }
        else
        {
            Text t = textObj.AddComponent<Text>();
            t.text = label;
            t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            t.fontSize = fontSize;
            t.alignment = TextAnchor.MiddleCenter;
            t.color = Color.white;
            t.fontStyle = FontStyle.Bold;
        }

        RectTransform textRt = textObj.GetComponent<RectTransform>();
        textRt.anchorMin = Vector2.zero;
        textRt.anchorMax = Vector2.one;
        textRt.sizeDelta = Vector2.zero;

        action(btn, tmpText);
    }

    private static void CreateTriggerButton(Transform parent, string name, string label, Vector2 pos, Vector2 size, System.Action<bool> action, int fontSize, bool zoomOut = false)
    {
        GameObject btnObj = new GameObject(name);
        btnObj.transform.SetParent(parent, false);

        Image img = btnObj.AddComponent<Image>();
        img.color = zoomOut ? new Color32(0, 51, 0, 204) : (label == "+" ? new Color32(0, 51, 0, 204) : new Color32(0, 0, 51, 204));

        EventTrigger trigger = btnObj.AddComponent<EventTrigger>();
        RectTransform rt = btnObj.GetComponent<RectTransform>();
        rt.anchoredPosition = pos;
        rt.sizeDelta = size;

        GameObject textObj = new GameObject("Text");
        textObj.transform.SetParent(btnObj.transform, false);
        Text t = textObj.AddComponent<Text>();
        t.text = label;
        t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.fontSize = fontSize;
        t.alignment = TextAnchor.MiddleCenter;
        t.color = Color.white;

        RectTransform textRt = textObj.GetComponent<RectTransform>();
        textRt.anchorMin = Vector2.zero;
        textRt.anchorMax = Vector2.one;
        textRt.sizeDelta = Vector2.zero;

        // Pointer Down
        var downEntry = new EventTrigger.Entry { eventID = EventTriggerType.PointerDown };
        UnityEventTools.AddBoolPersistentListener(downEntry.callback, new UnityEngine.Events.UnityAction<bool>(action), true);
        trigger.triggers.Add(downEntry);

        // Pointer Up
        var upEntry = new EventTrigger.Entry { eventID = EventTriggerType.PointerUp };
        UnityEventTools.AddBoolPersistentListener(upEntry.callback, new UnityEngine.Events.UnityAction<bool>(action), false);
        trigger.triggers.Add(upEntry);
    }

    private static void SetAnchor(RectTransform rt, TextAnchor anchor)
    {
        switch (anchor)
        {
            case TextAnchor.UpperLeft:
                rt.anchorMin = new Vector2(0, 1);
                rt.anchorMax = new Vector2(0, 1);
                rt.pivot = new Vector2(0.5f, 1f);
                break;
            case TextAnchor.UpperRight:
                rt.anchorMin = new Vector2(1, 1);
                rt.anchorMax = new Vector2(1, 1);
                rt.pivot = new Vector2(0.5f, 1f);
                break;
            case TextAnchor.LowerLeft:
                rt.anchorMin = new Vector2(0, 0);
                rt.anchorMax = new Vector2(0, 0);
                rt.pivot = new Vector2(0.5f, 0f);
                break;
            case TextAnchor.LowerRight:
                rt.anchorMin = new Vector2(1, 0);
                rt.anchorMax = new Vector2(1, 0);
                rt.pivot = new Vector2(0.5f, 0f);
                break;
            case TextAnchor.LowerCenter:
                rt.anchorMin = new Vector2(0.5f, 0);
                rt.anchorMax = new Vector2(0.5f, 0);
                rt.pivot = new Vector2(0.5f, 0f);
                break;
        }
    }
}
#endif
