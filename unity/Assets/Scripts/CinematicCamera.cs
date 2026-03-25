using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class CinematicCamera : MonoBehaviour
{
    public CameraController camCtrl;
    public float outsideApproachDist = 80f;
    public float inspectDwellNormal  = 3f;
    public float inspectDwellBottleneck = 7f;

    private bool      isRunning;
    private Coroutine tourCoroutine;
    private Vector3   camVelocity = Vector3.zero;

    public bool IsRunning => isRunning;

    public void StartCinematic() {
        if (tourCoroutine != null)
            StopCoroutine(tourCoroutine);
        isRunning = true;
        tourCoroutine = StartCoroutine(RunTour());
    }

    public void StopCinematic() {
        isRunning = false;
        if (tourCoroutine != null) {
            StopCoroutine(tourCoroutine);
            tourCoroutine = null;
        }
    }

    IEnumerator RunTour()
    {
        while (isRunning)
        {
            MachineVisual[] machines =
                FindObjectsByType<MachineVisual>(FindObjectsSortMode.None);
            if (machines == null ||
                machines.Length == 0)
            {
                yield return new WaitForSeconds(1f);
                continue;
            }

            Bounds b = GetBounds(machines);
            Vector3 center = b.center;
            float   size   = Mathf.Max(
                b.size.x, b.size.z, 20f);

            // PHASE 0 — outside fast approach
            yield return StartCoroutine(
                Phase0_OutsideApproach(
                    center, size));
            if (!isRunning) break;

            // PHASE 1 — enter and slow down
            yield return StartCoroutine(
                Phase1_EnterFactory(
                    center, size));
            if (!isRunning) break;

            // PHASE 2 — top overview
            yield return StartCoroutine(
                Phase2_TopOverview(
                    center, size));
            if (!isRunning) break;

            // PHASE 3+4 — row walk + inspect
            // Sort machines by row (Z) then
            // column (X) within each row
            var rows = GroupByRow(machines);
            yield return StartCoroutine(
                Phase3And4_SupervisorWalk(
                    rows, size));
            if (!isRunning) break;

            yield return new WaitForSeconds(2f);
        }
    }

    // Phase 0: start far outside, move fast
    IEnumerator Phase0_OutsideApproach(
        Vector3 center, float size)
    {
        Vector3 startPos = center +
            new Vector3(0f,
                size * 0.6f,
                -(size + outsideApproachDist));

        transform.position = startPos;
        transform.LookAt(center);

        Vector3 targetPos = center +
            new Vector3(0f,
                size * 0.5f,
                -(size * 0.6f));

        float elapsed = 0f;
        float duration = 3f;

        while (elapsed < duration && isRunning)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            // Fast lerp — no smoothdamp
            transform.position = Vector3.Lerp(
                startPos, targetPos,
                t * t); // ease-in
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(
                    center - transform.position),
                Time.deltaTime * 3f);
            yield return null;
        }
    }

    // Phase 1: enter factory, decelerate
    IEnumerator Phase1_EnterFactory(
        Vector3 center, float size)
    {
        Vector3 target = center +
            new Vector3(0f, size * 0.4f, 0f);
        float elapsed = 0f;
        float duration = 3f;

        while (elapsed < duration && isRunning)
        {
            elapsed += Time.deltaTime;
            // SmoothDamp for natural deceleration
            transform.position = Vector3.SmoothDamp(
                transform.position,
                target,
                ref camVelocity,
                1.2f);
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(
                    center - transform.position +
                    Vector3.up * 0.1f),
                Time.deltaTime * 2f);
            yield return null;
        }
    }

    // Phase 2: top view slow rotation
    IEnumerator Phase2_TopOverview(
        Vector3 center, float size)
    {
        Vector3 topPos = center +
            Vector3.up *
            Mathf.Clamp(size * 0.55f, 15f, 60f);

        // Smooth move to top position
        float moveTime = 0f;
        while (moveTime < 2.5f && isRunning)
        {
            moveTime += Time.deltaTime;
            transform.position = Vector3.SmoothDamp(
                transform.position, topPos,
                ref camVelocity, 0.6f);
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(
                    center - transform.position),
                Time.deltaTime * 2f);
            yield return null;
        }

        // Slow 180 degree rotation overview
        float rotTime = 0f;
        float rotDur  = 6f;
        float startYaw = camCtrl != null
            ? camCtrl.yaw : 0f;

        while (rotTime < rotDur && isRunning)
        {
            rotTime += Time.deltaTime;
            float angle = (rotTime / rotDur) * 180f;
            Vector3 rotPos = center + Quaternion.Euler(
                88f, startYaw + angle, 0f) *
                new Vector3(0f, 0f,
                    -(topPos - center).magnitude);
            transform.position = Vector3.SmoothDamp(
                transform.position, rotPos,
                ref camVelocity, 0.4f);
            transform.LookAt(center);
            yield return null;
        }
    }

    // Phase 3+4: walk each row then inspect
    IEnumerator Phase3And4_SupervisorWalk(
        List<List<MachineVisual>> rows,
        float size)
    {
        foreach (var row in rows)
        {
            if (!isRunning) yield break;
            if (row.Count == 0) continue;

            // Sort row left to right by X
            row.Sort((a, b) =>
                a.transform.position.x
                .CompareTo(
                b.transform.position.x));

            Vector3 rowStart =
                row[0].transform.position;
            Vector3 rowEnd   =
                row[row.Count-1]
                .transform.position;
            float   rowZ     = rowStart.z;

            // Walk camera along this row
            float walkHeight = 4f;
            Vector3 walkFrom = new Vector3(
                rowStart.x - 5f,
                walkHeight, rowZ);
            Vector3 walkTo   = new Vector3(
                rowEnd.x + 5f,
                walkHeight, rowZ);

            float walkDist =
                Vector3.Distance(walkFrom, walkTo);
            float walkDur  =
                Mathf.Clamp(walkDist * 0.25f,
                    4f, 15f);
            float walked   = 0f;

            while (walked < walkDur && isRunning)
            {
                walked += Time.deltaTime;
                float t = walked / walkDur;
                Vector3 walkTarget = Vector3.Lerp(
                    walkFrom, walkTo, t);

                transform.position = Vector3.SmoothDamp(
                    transform.position,
                    walkTarget,
                    ref camVelocity, 0.6f);

                // Look slightly ahead in walk dir
                Vector3 lookAhead = Vector3.Lerp(
                    walkFrom, walkTo,
                    Mathf.Clamp01(t + 0.15f));
                lookAhead.y = 1.5f;
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    Quaternion.LookRotation(
                        lookAhead - transform.position),
                    Time.deltaTime * 2f);

                yield return null;
            }

            // Inspect each machine in this row
            foreach (var m in row)
            {
                if (!isRunning) yield break;
                bool isBn = m.IsBottleneck;
                float dwell = isBn
                    ? inspectDwellBottleneck
                    : inspectDwellNormal;
                float dist  = isBn ? 5f : 7f;

                yield return StartCoroutine(
                    InspectMachine(m, dwell, dist));
            }
        }
    }

    IEnumerator InspectMachine(
        MachineVisual m,
        float dwell, float orbitDist)
    {
        Vector3 mPos =
            m.transform.position + Vector3.up * 1.5f;
        float elapsed   = 0f;
        float startYaw  = 0f;
        float orbitDeg  = m.IsBottleneck
            ? 200f : 90f;

        while (elapsed < dwell && isRunning)
        {
            elapsed += Time.deltaTime;
            float t   = elapsed / dwell;
            float yaw = startYaw + t * orbitDeg;

            Vector3 orbitOffset =
                Quaternion.Euler(18f, yaw, 0f) *
                new Vector3(0f, 0f, -orbitDist);

            // Bottleneck: add slight bob
            float bob = m.IsBottleneck
                ? Mathf.Sin(elapsed * 3f) * 0.15f
                : 0f;

            Vector3 target = mPos + orbitOffset +
                Vector3.up * bob;

            transform.position = Vector3.SmoothDamp(
                transform.position, target,
                ref camVelocity, 0.3f);
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(
                    mPos - transform.position),
                Time.deltaTime * 3f);

            yield return null;
        }
    }

    // Group machines by station row
    // Rows = sorted by Z position
    List<List<MachineVisual>> GroupByRow(
        MachineVisual[] machines)
    {
        var rowMap =
            new Dictionary<int, List<MachineVisual>>();

        foreach (var m in machines)
        {
            // Round Z to nearest machineStep (12f)
            // to group same-row machines
            int rowKey = Mathf.RoundToInt(
                m.transform.position.z / 12f);
            if (!rowMap.ContainsKey(rowKey))
                rowMap[rowKey] =
                    new List<MachineVisual>();
            rowMap[rowKey].Add(m);
        }

        // Sort rows by Z (ascending)
        var sortedKeys =
            new List<int>(rowMap.Keys);
        sortedKeys.Sort();

        var result =
            new List<List<MachineVisual>>();
        foreach (var k in sortedKeys)
            result.Add(rowMap[k]);

        return result;
    }

    Bounds GetBounds(MachineVisual[] machines)
    {
        Bounds b = new Bounds(
            machines[0].transform.position,
            Vector3.zero);
        foreach (var m in machines)
            b.Encapsulate(m.transform.position);
        return b;
    }
}
