package com.factory.digitaltwin.unity

import android.content.Context
import android.content.Intent
import android.util.Log
import com.factory.digitaltwin.model.MachineConfig
import com.factory.digitaltwin.ui.unity.Unity3DActivity
import org.json.JSONArray
import org.json.JSONObject

object UnityBridge {

    private const val TAG = "UnityBridge"

    /**
     * Launch Unity 3D factory view.
     * Call from any Fragment or Activity.
     *
     * Example usage in BottleneckFragment:
     *   UnityBridge.launch(
     *     context  = requireContext(),
     *     machines = viewModel.getSelectedMachines(),
     *     demand   = viewModel.demandUnits,
     *     shift    = viewModel.shiftHours,
     *     workers  = viewModel.numWorkers
     *   )
     */
    fun launch(
        context: Context,
        machines: List<MachineConfig>,
        demand:   Int   = 200,
        shift:    Float = 8f,
        workers:  Int   = 2,
        stationResultsJson: String? = null
    ) {
        if (machines.isEmpty()) {
            Log.w(TAG,
                "No machines configured." +
                " Cannot launch Unity.")
            return
        }

        try {
            val configJson = buildConfigJson(
                machines = machines,
                demand   = demand,
                shift    = shift,
                workers  = workers
            )

            Log.d(TAG,
                "Launching Unity 3D view." +
                " Machines: ${machines.size}" +
                " Total: ${machines.sumOf { it.count }}")

            val intent = Intent(
                context,
                Unity3DActivity::class.java
            )
            // Force fresh activity — no reuse
            intent.addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_CLEAR_TOP or
                Intent.FLAG_ACTIVITY_SINGLE_TOP
            )
            intent.putExtra(
                Unity3DActivity.EXTRA_CONFIG_JSON,
                configJson
            )
            if (!stationResultsJson.isNullOrEmpty()) {
                intent.putExtra(
                    Unity3DActivity.EXTRA_STATION_DATA,
                    stationResultsJson
                )
            }
            context.startActivity(intent)

        } catch (e: Exception) {
            Log.e(TAG,
                "Failed to launch Unity: " +
                e.message)
        }
    }

    /**
     * Build factory config JSON for Unity.
     * Schema matches what MachineSpawner.cs
     * expects in BuildFactory().
     */
    fun buildConfigJson(
        machines: List<MachineConfig>,
        demand:   Int,
        shift:    Float,
        workers:  Int
    ): String {
        val root = JSONObject()
        root.put("factory_name", "My Factory")
        root.put("factory_type", "lathe")
        root.put("shift_hours",  shift)
        root.put("num_operators", workers)
        root.put("language", "en")
        root.put("mode", "static")
        root.put("demand_units", demand)

        val stations = JSONArray()
        var stationId = 1

        Log.d("UnityBridge",
            "buildConfigJson called." +
            " Input machines: " +
            machines.map {
                "${it.nameEn}×${it.count}"
            }.joinToString(", "))

        // Only include machines with count > 0
        val selected = machines
            .filter { it.count > 0 }

        Log.d("UnityBridge",
            "After filter: " +
            selected.map {
                "${it.nameEn}×${it.count}"
            }.joinToString(", "))

        selected.forEachIndexed { index, m ->
            val s = JSONObject()
            s.put("id",            stationId)
            s.put("name",          m.nameEn)
            s.put("name_ta",       m.nameTa)
            s.put("icon",          m.id)
            s.put("num_machines",  m.count)
            s.put("workflow_order", index + 1)
            s.put("cycle_time_sec", m.cycleTimeSec)
            s.put("mtbf_hours",    m.mtbfHours)
            s.put("mttr_hours",    m.mttrHours)
            s.put("setup_minutes", m.setupMinutes)
            s.put("variability",   m.variability)
            // Position — spawner calculates
            // actual grid position internally
            s.put("position_x",
                (index * 20).toFloat())
            s.put("position_z", 0f)
            stations.put(s)
            stationId++
        }

        root.put("stations", stations)
        root.put("timestamp",
            System.currentTimeMillis())
        return root.toString()
    }

    /**
     * Build station results JSON for Unity
     * after simulation runs.
     * Matches StationMetric class in Unity.
     */
    fun buildStationResultsJson(
        machines: List<MachineConfig>,
        bottleneckId: Int = -1,
        metricsJson: String = ""
    ): String {
        if (metricsJson.isNotEmpty()) {
            return metricsJson
        }
        val array = JSONArray()
        var id = 1
        machines.filter { it.count > 0 }.forEach { m ->
            val s = JSONObject()
            s.put("station_id",    id)
            s.put("station_name",  m.nameEn)
            s.put("utilization",   0.75f)
            s.put("queue_length",  0)
            s.put("bni",           0.0f)
            s.put("is_bottleneck", id == bottleneckId)
            s.put("status",        "running")
            array.put(s)
            id++
        }
        return array.toString()
    }
}
