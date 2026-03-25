package com.factory.digitaltwin.model

data class MachineConfig(
    val id: String,
    val stationId: Int = 0,
    val nameEn: String,
    val nameTa: String,
    val emoji: String,
    var count: Int = 0,
    var cycleTimeSec: Int = 45,
    var mtbfHours: Float = 8.0f,
    var mttrHours: Float = 0.5f,
    var setupMinutes: Int = 10,
    var variability: Float = 0.15f
)

data class SimulationInput(
    val machines: List<MachineConfig>,
    val demandUnits: Int,
    val shiftHours: Float,
    val numWorkers: Int,
    val machineCondition: String
)
