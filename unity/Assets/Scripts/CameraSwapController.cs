using System;
using System.Collections;
using UnityEngine;

public class CameraSwapController : MonoBehaviour
{
    [Serializable]
    public class CameraView
    {
        public string title = "View";
        public Camera camera;
        public KeyCode shortcut = KeyCode.None;
    }

    [Header("Assign Scene Cameras Here")]
    public CameraView[] views = new CameraView[4];

    [Header("Transition Settings")]
    public bool enableTransitions = true;
    [Range(0.1f, 2f)]
    public float transitionDuration = 0.5f;
    public AnimationCurve transitionCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);

    private GUIStyle labelStyle;
    private int currentViewIndex = 0;
    private bool isTransitioning = false;
    private float transitionProgress = 0f;
    private Coroutine transitionCoroutine;

    private void Start()
    {
        ApplyLayout();
    }

    private void OnEnable()
    {
        ApplyLayout();
    }

    private void OnDisable()
    {
        if (transitionCoroutine != null)
        {
            StopCoroutine(transitionCoroutine);
            transitionCoroutine = null;
        }
    }

    private void Update()
    {
        HandleKeyboardInput();
    }

    private void HandleKeyboardInput()
    {
        // Check for shortcut keys
        for (int i = 0; i < views.Length; i++)
        {
            if (!IsAssignedView(i) || views[i].shortcut == KeyCode.None)
            {
                continue;
            }

            if (Input.GetKeyDown(views[i].shortcut))
            {
                SwitchToCamera(i);
                return;
            }
        }

        // Check for cycle key (C to cycle through cameras)
        if (Input.GetKeyDown(KeyCode.C) && !isTransitioning)
        {
            CycleToNextCamera();
        }
    }

    public void SwitchToCamera(int viewIndex)
    {
        if (!IsValidIndex(viewIndex) || !IsAssignedView(viewIndex) || viewIndex == currentViewIndex)
        {
            return;
        }

        if (enableTransitions && !isTransitioning)
        {
            if (transitionCoroutine != null)
            {
                StopCoroutine(transitionCoroutine);
            }
            transitionCoroutine = StartCoroutine(TransitionToCamera(viewIndex));
        }
        else
        {
            currentViewIndex = viewIndex;
            ApplyLayout();
        }
    }

    public void CycleToNextCamera()
    {
        int assignedCount = GetAssignedViewCount();
        if (assignedCount <= 1)
        {
            return;
        }

        int nextIndex = currentViewIndex + 1;
        
        // Find next assigned camera
        while (nextIndex < views.Length && !IsAssignedView(nextIndex))
        {
            nextIndex++;
        }

        // Loop back to start if we've reached the end
        if (nextIndex >= views.Length)
        {
            nextIndex = 0;
            while (nextIndex < views.Length && !IsAssignedView(nextIndex))
            {
                nextIndex++;
            }
        }

        SwitchToCamera(nextIndex);
    }

    private IEnumerator TransitionToCamera(int viewIndex)
    {
        isTransitioning = true;
        transitionProgress = 0f;
        int previousIndex = currentViewIndex;

        while (transitionProgress < transitionDuration)
        {
            transitionProgress += Time.deltaTime;
            float normalizedProgress = Mathf.Clamp01(transitionProgress / transitionDuration);
            float easedProgress = transitionCurve.Evaluate(normalizedProgress);

            // Fade out old camera
            if (IsAssignedView(previousIndex) && views[previousIndex].camera != null)
            {
                Color bgColor = views[previousIndex].camera.backgroundColor;
                bgColor.a = 1f - easedProgress;
                views[previousIndex].camera.backgroundColor = bgColor;
            }

            yield return null;
        }

        currentViewIndex = viewIndex;
        ApplyLayout();
        transitionProgress = 0f;
        isTransitioning = false;
    }

    public void ApplyLayout()
    {
        // Enable only the current camera, disable all others
        for (int i = 0; i < views.Length; i++)
        {
            if (!IsAssignedView(i))
            {
                continue;
            }

            bool isActive = i == currentViewIndex;
            views[i].camera.rect = new Rect(0, 0, 1, 1);
            views[i].camera.enabled = isActive;

            // Reset background alpha
            Color bgColor = views[i].camera.backgroundColor;
            bgColor.a = 1f;
            views[i].camera.backgroundColor = bgColor;
        }

        UpdateActiveCameraBindings();
    }

    private void UpdateActiveCameraBindings()
    {
        for (int i = 0; i < views.Length; i++)
        {
            if (!IsAssignedView(i))
            {
                continue;
            }

            Camera cameraComponent = views[i].camera;
            bool isPrimary = i == currentViewIndex;

            cameraComponent.tag = isPrimary ? "MainCamera" : "Untagged";

            AudioListener audioListener = cameraComponent.GetComponent<AudioListener>();
            if (audioListener != null)
            {
                audioListener.enabled = isPrimary;
            }
        }
    }

    private int GetAssignedViewCount()
    {
        int count = 0;
        for (int i = 0; i < views.Length; i++)
        {
            if (IsAssignedView(i))
            {
                count++;
            }
        }
        return count;
    }

    private bool IsAssignedView(int index)
    {
        return IsValidIndex(index) && views[index] != null && views[index].camera != null;
    }

    private bool IsValidIndex(int index)
    {
        return index >= 0 && index < views.Length;
    }

    private void OnGUI()
    {
        if (!IsAssignedView(currentViewIndex))
        {
            return;
        }

        if (labelStyle == null)
        {
            labelStyle = new GUIStyle(GUI.skin.box);
            labelStyle.alignment = TextAnchor.MiddleCenter;
            labelStyle.fontSize = 15;
            labelStyle.normal.textColor = Color.white;
        }

        string title = string.IsNullOrWhiteSpace(views[currentViewIndex].title)
            ? views[currentViewIndex].camera.name
            : views[currentViewIndex].title;

        // Show transition indicator
        if (isTransitioning)
        {
            title += $" ({transitionProgress / transitionDuration * 100:F0}%)";
        }

        Rect labelRect = new Rect(10f, 10f, 200f, 40f);
        GUI.Box(labelRect, title, labelStyle);
    }
}
