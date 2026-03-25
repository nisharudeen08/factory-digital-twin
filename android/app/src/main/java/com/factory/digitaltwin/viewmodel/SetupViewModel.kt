package com.factory.digitaltwin.viewmodel

import androidx.lifecycle.ViewModel
import com.factory.digitaltwin.model.MachineConfig
import com.factory.digitaltwin.model.SimulationInput
import org.json.JSONArray
import org.json.JSONObject

class SetupViewModel : ViewModel() {
    // All available Lathe factory machines
    val availableMachines = mutableListOf(
        MachineConfig(
            id = "lathe",
            stationId = 1,
            nameEn = "Lathe Machine",
            nameTa = "தட்டு இயந்திரம்",
            emoji = "⚙️",
            cycleTimeSec = 45,
            mtbfHours = 8.0f,
            mttrHours = 0.5f,
            setupMinutes = 10
        ),
        MachineConfig(
            id = "cnc",
            stationId = 2,
            nameEn = "CNC Milling",
            nameTa = "சி.என்.சி. மில்லிங்",
            emoji = "🔧",
            cycleTimeSec = 60,
            mtbfHours = 12.0f,
            mttrHours = 0.5f,
            setupMinutes = 15
        ),
        MachineConfig(
            id = "drill",
            stationId = 3,
            nameEn = "Drill Press",
            nameTa = "துளையிடும் இயந்திரம்",
            emoji = "🔩",
            cycleTimeSec = 30,
            mtbfHours = 10.0f,
            mttrHours = 0.3f,
            setupMinutes = 5
        ),
        MachineConfig(
            id = "weld",
            stationId = 4,
            nameEn = "Welding Station",
            nameTa = "வெல்டிங் நிலையம்",
            emoji = "🔥",
            cycleTimeSec = 55,
            mtbfHours = 6.0f,
            mttrHours = 0.8f,
            setupMinutes = 12
        ),
        MachineConfig(
            id = "grind",
            stationId = 5,
            nameEn = "Surface Grinder",
            nameTa = "அரைக்கும் இயந்திரம்",
            emoji = "⚡",
            cycleTimeSec = 40,
            mtbfHours = 10.0f,
            mttrHours = 0.4f,
            setupMinutes = 8
        ),
        MachineConfig(
            id = "band_saw",
            stationId = 6,
            nameEn = "Band Saw",
            nameTa = "பேண்ட் சா",
            emoji = "🪚",
            cycleTimeSec = 35,
            mtbfHours = 10.0f,
            mttrHours = 0.3f,
            setupMinutes = 6
        ),
        MachineConfig(
            id = "qc",
            stationId = 7,
            nameEn = "QC Inspection",
            nameTa = "தர சரிபார்ப்பு",
            emoji = "🔍",
            cycleTimeSec = 25,
            mtbfHours = 20.0f,
            mttrHours = 0.2f,
            setupMinutes = 3
        )
    )

    // Simulation parameters — set by user on Screen 4
    var demandUnits: Int = 200
    var shiftHours: Float = 8f
    var numWorkers: Int = 2
    var machineCondition: String = "average"

    // Simulation History / Results
    var lastSimulationResult: String = ""
    var lastThroughput: Float = 0f
    var lastStationMetrics: String = ""
    var lastBottleneckId: Int = -1

    // Tracks which machine we are editing params for
    var currentParamIndex: Int = 0

    // Returns only machines the user added (count > 0)
    fun getSelectedMachines(): List<MachineConfig> {
        // Always read from current live data
        // Never cache this result
        return availableMachines.filter { it.count > 0 }
    }

    // Total count across all machine types
    fun getTotalMachines(): Int =
        availableMachines.sumOf { it.count }

    // Total station types selected
    fun getTotalStationTypes(): Int =
        availableMachines.count { it.count > 0 }

    // Build final input object for Python API
    fun buildSimulationInput(): SimulationInput =
        SimulationInput(
            machines = getSelectedMachines(),
            demandUnits = demandUnits,
            shiftHours = shiftHours,
            numWorkers = numWorkers,
            machineCondition = machineCondition
        )

    /**
     * Generate JSON string representing station metrics for Unity visualization.
     * Matches Unity's StationMetric structure.
     */
    fun getUnitySimulationJson(): String {
        val selected = getSelectedMachines()
        if (selected.isEmpty()) return "{\"items\":[]}"

        val items = JSONArray()
        
        // Find bottleneck for highlighting logic
        val bottleneck = selected.maxByOrNull {
            it.cycleTimeSec.toFloat() / it.count
        }

        val shiftSecs = shiftHours * 3600f

        for (m in selected) {
            val station = JSONObject()
            
            // Basic identification
            station.put("id", m.stationId)
            station.put("name", m.nameEn)
            station.put("name_ta", m.nameTa)

            // Calculation (Mock simulation logic matching BottleneckFragment)
            val demandPerMachine = demandUnits.toFloat() / m.count.toFloat()
            val timeNeeded = demandPerMachine * m.cycleTimeSec
            val utilPct = ((timeNeeded / shiftSecs)).coerceIn(0f, 1f)
            
            station.put("utilization", utilPct)
            
            // Queue length (simplified)
            val excessJobs = if (utilPct > 0.85f) ((utilPct - 0.85f) * demandUnits).toInt() else 0
            station.put("queue", excessJobs)
            
            // Bottle Neck Index (simplified)
            val bni = (utilPct * 0.95f).coerceIn(0f, 0.99f)
            station.put("bni", bni)
            
            station.put("is_bottleneck", m == bottleneck)
            
            // Status string based on utilization
            val status = when {
                utilPct > 0.9f -> "critical"
                utilPct > 0.7f -> "warning"
                else -> "running"
            }
            station.put("status", status)

            items.put(station)
        }

        val result = JSONObject()
        result.put("items", items)
        return result.toString()
    }

    // Reset all machine counts to 0
    fun resetMachines() {
        availableMachines.forEach { it.count = 0 }
        currentParamIndex = 0
    }
}

