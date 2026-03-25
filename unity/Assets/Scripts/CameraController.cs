using UnityEngine;

public class CameraController : MonoBehaviour
{
    [Header("Orbit")]
    public float distance    = 60f;
    public float minDistance = 8f;
    public float maxDistance = 500f;
    public float pitch       = 38f;
    public float yaw         = 0f;

    [Header("Sensitivity")]
    public float orbitSensitivity = 0.25f;
    public float pinchSpeed       = 0.15f;
    public float panSpeed         = 0.055f;

    [Header("Joystick")]
    public VirtualJoystick joystick;

    private Vector3 targetPosition = Vector3.zero;

    // Single touch / mouse orbit state
    private Vector2 lastDragPos;

    // Mouse pan state
    private Vector3 lastMousePos;
    private bool    isMousePanning  = false;



    void LateUpdate()
    {
        HandleJoystick();
        HandlePinchZoom();
        HandleMouse();
        ApplyCameraTransform();
    }

    private void HandleJoystick()
    {
        if (joystick == null)
        {
            Debug.LogWarning(
                "[Camera] joystick is NULL");
            return;
        }

        if (!joystick.IsActive) return;

        float h = joystick.Direction.x;
        float v = joystick.Direction.y;

        yaw   += h * orbitSensitivity
                 * 120f * Time.deltaTime;
        pitch -= v * orbitSensitivity
                 * 120f * Time.deltaTime;
        pitch  = Mathf.Clamp(pitch, 5f, 88f);

        Debug.Log(
            "[Camera] Joystick: " +
            joystick.Direction +
            " yaw=" + yaw +
            " pitch=" + pitch);
    }

    private void HandlePinchZoom()
    {
        if (Input.touchCount != 2) return;

        Touch t0 = Input.GetTouch(0);
        Touch t1 = Input.GetTouch(1);

        // Skip if touching UI elements
        if (IsPointerOverUI(t0.position) ||
            IsPointerOverUI(t1.position))
            return;

        Vector2 prev0 =
            t0.position - t0.deltaPosition;
        Vector2 prev1 =
            t1.position - t1.deltaPosition;

        float prevDist =
            Vector2.Distance(prev0, prev1);
        float currDist =
            Vector2.Distance(
                t0.position, t1.position);

        float pinchDelta = prevDist - currDist;
        distance += pinchDelta * pinchSpeed;
        distance  = Mathf.Clamp(
            distance, minDistance, maxDistance);
    }

    private bool IsPointerOverUI(
        Vector2 screenPos)
    {
        var eventData =
            new UnityEngine.EventSystems
                .PointerEventData(
                UnityEngine.EventSystems
                    .EventSystem.current)
        {
            position = screenPos
        };

        var results =
            new System.Collections.Generic
                .List<UnityEngine.EventSystems
                    .RaycastResult>();

        UnityEngine.EventSystems
            .EventSystem.current
            .RaycastAll(eventData, results);

        return results.Count > 0;
    }

    // ── MOUSE (Editor / PC) ──────────────────────────
    void HandleMouse()
    {
        // Right mouse — orbit
        if (Input.GetMouseButtonDown(1))
        {
            lastMousePos   = Input.mousePosition;
            isMousePanning = false;
        }
        if (Input.GetMouseButton(1))
        {
            Vector3 delta =
                Input.mousePosition - lastMousePos;
            yaw   += delta.x * orbitSensitivity;
            pitch -= delta.y * orbitSensitivity;
            pitch  = Mathf.Clamp(pitch, 5f, 88f);
            lastMousePos = Input.mousePosition;
        }

        // Middle mouse — pan
        if (Input.GetMouseButtonDown(2))
        {
            lastMousePos   = Input.mousePosition;
            isMousePanning = true;
        }
        if (Input.GetMouseButton(2) && isMousePanning)
        {
            Vector3 delta =
                Input.mousePosition - lastMousePos;
            targetPosition +=
                transform.right * delta.x * panSpeed;
            targetPosition +=
                transform.up    * delta.y * panSpeed;
            lastMousePos = Input.mousePosition;
        }
        if (Input.GetMouseButtonUp(2))
            isMousePanning = false;

        // Scroll — zoom
        float scroll =
            Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.001f)
        {
            distance -= scroll * distance * 0.4f;
            distance  = Mathf.Clamp(
                distance, minDistance, maxDistance);
        }
    }

    // ── APPLY ────────────────────────────────────────
    void ApplyCameraTransform()
    {
        distance = Mathf.Clamp(
            distance, minDistance, maxDistance);
        Quaternion rot =
            Quaternion.Euler(pitch, yaw, 0f);
        Vector3 offset =
            rot * new Vector3(0f, 0f, -distance);
        Vector3 camPos = targetPosition + offset;

        // No Y clamp — let orbit math work freely
        // FocusOnFactory sets correct start position

        transform.position = camPos;
        transform.LookAt(
            targetPosition + Vector3.up * 1f);
    }

    // ── PUBLIC ───────────────────────────────────────
    public void SetTarget(Vector3 position)
    {
        targetPosition = position;
    }

    public void FocusOnFactory()
    {
        MachineVisual[] machines =
            Object.FindObjectsByType<MachineVisual>(
            FindObjectsSortMode.None);
        if (machines == null ||
            machines.Length == 0)
        {
            Debug.LogWarning(
                "[Camera] No machines found.");
            return;
        }

        Bounds b = new Bounds(
            machines[0].transform.position,
            Vector3.zero);
        foreach (var m in machines)
            b.Encapsulate(m.transform.position);

        Vector3 center    = b.center;
        float   factoryW  = b.size.x + 16f;
        float   factoryD  = b.size.z + 16f;
        float   factorySize = Mathf.Max(
            factoryW, factoryD, 20f);

        // Set camera DIRECTLY — no orbit math
        // Camera positioned at edge of factory
        // looking inward and slightly down
        // This guarantees correct view every time

        // Camera sits at one end of factory
        // at human eye height (Y=5)
        // looking across floor toward machines
        float camX = center.x;
        float camY = Mathf.Clamp(
            factorySize * 0.12f, 4f, 8f);
        float camZ = center.z -
            Mathf.Clamp(factorySize * 0.55f,
                15f, 90f);

        transform.position =
            new Vector3(camX, camY, camZ);

        // Look at center of factory at
        // machine height (Y=1.5)
        transform.LookAt(new Vector3(
            center.x, 1.5f, center.z));

        // Sync orbit state to match
        // so joystick/zoom work correctly
        targetPosition = new Vector3(
            center.x, 1.5f, center.z);

        Vector3 diff =
            transform.position - targetPosition;
        distance = diff.magnitude;
        pitch    = 20f;
        yaw      = 0f;

        // Zoom limits
        minDistance = 8f;
        maxDistance = Mathf.Clamp(
            factorySize * 0.8f, 20f, 150f);

        Debug.Log(
            $"[Camera] Direct position focus:" +
            $" machines={machines.Length}" +
            $" camPos={transform.position}" +
            $" dist={distance:F1}" +
            $" factorySize={factorySize:F1}");
    }

    public void RefocusAfterRebuild()
    {
        // Camera position is set manually
        // in Inspector — do not auto-move it
        Debug.Log(
            "[Camera] RefocusAfterRebuild:" +
            " skipped — manual position active.");
    }

    private float GetMaxInsideDistance()
    {
        MachineVisual[] machines =
            Object.FindObjectsByType<MachineVisual>(
            FindObjectsSortMode.None);
        if (machines == null ||
            machines.Length == 0)
            return maxDistance;

        Bounds b = new Bounds(
            machines[0].transform.position,
            Vector3.zero);
        foreach (var m in machines)
            b.Encapsulate(m.transform.position);

        // Allow camera to pull back to
        // factory diagonal plus wall margin
        // Works correctly for any factory size
        float diagonal  = b.size.magnitude;
        float maxInside = (diagonal / 2f) + 8f;

        return Mathf.Max(maxInside,
            minDistance + 1f);
    }
}
