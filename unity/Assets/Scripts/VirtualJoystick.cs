using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class VirtualJoystick : MonoBehaviour,
    IPointerDownHandler,
    IPointerUpHandler,
    IDragHandler
{
    [Header("References")]
    [SerializeField]
    private RectTransform background;

    [SerializeField]
    private RectTransform handle;

    [Header("Settings")]
    [SerializeField]
    private float handleRange = 50f;

    public Vector2 Direction
        { get; private set; }

    public bool IsActive
        { get; private set; }

    private Vector2 joystickOrigin;
    private int     activeTouchId = -1;
    private RectTransform rectTransform;
    private Camera uiCamera;

    void Awake()
    {
        rectTransform = GetComponent<RectTransform>();
        
        // Find UI camera
        var canvas = GetComponentInParent<Canvas>();
        if (canvas != null)
            uiCamera = canvas.renderMode == 
                RenderMode.ScreenSpaceOverlay 
                ? null 
                : canvas.worldCamera;

        if (handle != null)
            handle.anchoredPosition = Vector2.zero;
        Direction = Vector2.zero;
        IsActive  = false;

        // Make sure background has raycast target
        var img = background
            ?.GetComponent<Image>();
        if (img != null)
            img.raycastTarget = true;
    }

    void Update()
    {
        // Raw touch fallback for Android
        // in case EventSystem events miss
        if (Input.touchCount > 0)
        {
            foreach (Touch touch in Input.touches)
            {
                if (touch.phase ==
                    TouchPhase.Began)
                {
                    if (IsTouchOnJoystick(
                        touch.position) &&
                        activeTouchId == -1)
                    {
                        activeTouchId =
                            touch.fingerId;
                        IsActive = true;
                        joystickOrigin =
                            background
                            .anchoredPosition;
                        UpdateHandle(
                            touch.position);
                    }
                }
                else if (
                    touch.phase ==
                        TouchPhase.Moved ||
                    touch.phase ==
                        TouchPhase.Stationary)
                {
                    if (touch.fingerId ==
                        activeTouchId)
                    {
                        UpdateHandle(
                            touch.position);
                    }
                }
                else if (
                    touch.phase ==
                        TouchPhase.Ended ||
                    touch.phase ==
                        TouchPhase.Canceled)
                {
                    if (touch.fingerId ==
                        activeTouchId)
                    {
                        ResetJoystick();
                    }
                }
            }
        }
    }

    private bool IsTouchOnJoystick(
        Vector2 screenPos)
    {
        return RectTransformUtility
            .RectangleContainsScreenPoint(
                rectTransform,
                screenPos,
                uiCamera);
    }

    private void UpdateHandle(
        Vector2 screenPos)
    {
        Vector2 localPoint;
        RectTransformUtility
            .ScreenPointToLocalPointInRectangle(
                background.parent
                    as RectTransform,
                screenPos,
                uiCamera,
                out localPoint);

        Vector2 delta =
            localPoint - joystickOrigin;

        Vector2 clamped =
            Vector2.ClampMagnitude(
                delta, handleRange);

        if (handle != null)
            handle.anchoredPosition = clamped;

        Direction = clamped / handleRange;
    }

    private void ResetJoystick()
    {
        activeTouchId = -1;
        IsActive      = false;
        Direction     = Vector2.zero;

        if (handle != null)
            handle.anchoredPosition =
                Vector2.zero;
    }

    // EventSystem handlers as backup
    public void OnPointerDown(
        PointerEventData e)
    {
        if (activeTouchId != -1) return;
        IsActive       = true;
        joystickOrigin =
            background.anchoredPosition;
        UpdateHandle(e.position);
    }

    public void OnDrag(PointerEventData e)
    {
        if (!IsActive) return;
        UpdateHandle(e.position);
    }

    public void OnPointerUp(
        PointerEventData e)
    {
        ResetJoystick();
    }
}
