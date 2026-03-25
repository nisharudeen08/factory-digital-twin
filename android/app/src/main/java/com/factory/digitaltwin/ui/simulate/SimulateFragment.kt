package com.factory.digitaltwin.ui.simulate

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import com.factory.digitaltwin.R
import com.factory.digitaltwin.SetupActivity
import com.factory.digitaltwin.databinding.FragmentSimulateBinding
import com.factory.digitaltwin.ui.bottleneck.BottleneckFragment
import com.factory.digitaltwin.viewmodel.SetupViewModel
import com.factory.digitaltwin.unity.UnityBridge
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import android.util.Log
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

class SimulateFragment : Fragment() {
    private var _binding: FragmentSimulateBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SetupViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSimulateBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        showConfigSummary()
        setupDemandChips()
        setupWorkerChips()
        setupShiftChips()
        setupConditionButtons()
        setupSimulateButton()

        // Hide button initially
        binding.btnPreview3d?.visibility = View.GONE
    }

    private fun showConfigSummary() {
        val selected = viewModel.getSelectedMachines()
        val total = viewModel.getTotalMachines()
        val summary = selected.joinToString("  ·  ") {
            "${it.count}× ${it.nameEn}"
        }
        binding.tvProjectedOutput.text = "—"
        android.util.Log.d("SimulateFragment", "Config: $summary | Total: $total machines")
    }

    private fun setupDemandChips() {
        val chips = listOf(
            Pair(binding.chipDemand100, 100),
            Pair(binding.chipDemand150, 150),
            Pair(binding.chipDemand200, 200),
            Pair(binding.chipDemand250, 250),
            Pair(binding.chipDemand300, 300)
        )
        selectChip(chips, binding.chipDemand200, viewModel.demandUnits)
        chips.forEach { (chip, value) ->
            chip.setOnClickListener {
                viewModel.demandUnits = value
                binding.tvDemandValue.text = value.toString()
                chips.forEach { (c, _) ->
                    c.setBackgroundResource(R.drawable.bg_chip_unselected)
                    c.setTextColor(resources.getColor(R.color.text_secondary, null))
                }
                chip.setBackgroundResource(R.drawable.bg_chip_selected)
                chip.setTextColor(resources.getColor(R.color.primary, null))
            }
        }
    }

    private fun setupWorkerChips() {
        val chips = listOf(
            Pair(binding.chipWorkers1, 1),
            Pair(binding.chipWorkers2, 2),
            Pair(binding.chipWorkers3, 3),
            Pair(binding.chipWorkers4, 4)
        )
        selectChip(chips, binding.chipWorkers2, viewModel.numWorkers)
        chips.forEach { (chip, value) ->
            chip.setOnClickListener {
                viewModel.numWorkers = value
                binding.tvWorkersValue.text = value.toString()
                chips.forEach { (c, _) ->
                    c.setBackgroundResource(R.drawable.bg_chip_unselected)
                    c.setTextColor(resources.getColor(R.color.text_secondary, null))
                }
                chip.setBackgroundResource(R.drawable.bg_chip_selected)
                chip.setTextColor(resources.getColor(R.color.primary, null))
            }
        }
    }

    private fun setupShiftChips() {
        val chips = listOf(
            Pair(binding.chipShift6h,  6f),
            Pair(binding.chipShift8h,  8f),
            Pair(binding.chipShift10h, 10f),
            Pair(binding.chipShift12h, 12f)
        )
        selectChip(chips, binding.chipShift8h, viewModel.shiftHours)
        chips.forEach { (chip, value) ->
            chip.setOnClickListener {
                viewModel.shiftHours = value
                binding.tvShiftValue.text = "${value.toInt()}h"
                chips.forEach { (c, _) ->
                    c.setBackgroundResource(R.drawable.bg_chip_unselected)
                    c.setTextColor(resources.getColor(R.color.text_secondary, null))
                }
                chip.setBackgroundResource(R.drawable.bg_chip_selected)
                chip.setTextColor(resources.getColor(R.color.primary, null))
            }
        }
    }

    private fun setupConditionButtons() {
        val buttons = listOf(
            Pair(binding.btnConditionGood,    "good"),
            Pair(binding.btnConditionAverage, "average"),
            Pair(binding.btnConditionPoor,    "poor")
        )
        binding.btnConditionAverage.setBackgroundResource(R.drawable.bg_chip_selected)
        buttons.forEach { (btn, value) ->
            btn.setOnClickListener {
                viewModel.machineCondition = value
                buttons.forEach { (b, _) ->
                    b.setBackgroundResource(R.drawable.bg_chip_unselected)
                }
                btn.setBackgroundResource(R.drawable.bg_chip_selected)
            }
        }
    }

    private fun setupSimulateButton() {
        binding.btnExecuteSimulation.setOnClickListener {
            runSimulation()
        }
        setupPreview3DButton()
    }

    private fun setupPreview3DButton() {
        binding.btnPreview3d?.setOnClickListener {

            // Read fresh data NOW
            // not from a cached variable
            val machines =
                viewModel.getSelectedMachines()
            val demand  = viewModel.demandUnits
            val shift   = viewModel.shiftHours
            val workers = viewModel.numWorkers

            Log.d("SimulateFragment",
                "Launching Unity with: " +
                "${machines.size} types, " +
                "total=${machines.sumOf{it.count}}")

            if (machines.isEmpty() ||
                machines.sumOf { it.count } == 0)
            {
                Toast.makeText(
                    requireContext(),
                    "Please add machines first.",
                    Toast.LENGTH_SHORT
                ).show()
                return@setOnClickListener
            }

            UnityBridge.launch(
                context  = requireContext(),
                machines = machines,
                demand   = demand,
                shift    = shift,
                workers  = workers
            )
        }
    }

    companion object {
        // Render.com free cloud server
        // Works on any network anywhere
        const val PYTHON_SERVER_URL = "https://factory-twin-server.onrender.com"
    }

    private fun runSimulation() {
        if (viewModel.getTotalMachines() == 0) {
            Toast.makeText(requireContext(),
                "No machines configured. Go back and add machines.",
                Toast.LENGTH_LONG).show()
            return
        }

        binding.btnExecuteSimulation.isEnabled = false
        binding.layoutLoading.visibility = View.VISIBLE

        lifecycleScope.launch {
            try {
                // Step 1: POST config to Python
                val configJson = UnityBridge.buildConfigJson(
                    machines = viewModel.getSelectedMachines(),
                    demand   = viewModel.demandUnits,
                    shift    = viewModel.shiftHours,
                    workers  = viewModel.numWorkers
                )

                val configSent = withContext(Dispatchers.IO) {
                    postJson(
                        url  = "$PYTHON_SERVER_URL/config",
                        json = configJson
                    )
                }

                if (!configSent) {
                    showError("Cannot reach Python server at $PYTHON_SERVER_URL. Check your IP and make sure Python is running.")
                    return@launch
                }

                android.util.Log.d("SimulateFragment", "Config sent successfully")

                // Step 2: POST simulate to Python
                val simulateBody = buildSimulateRequestJson()

                val resultJson = withContext(Dispatchers.IO) {
                    postJsonAndGetResponse(
                        url  = "$PYTHON_SERVER_URL/simulate",
                        json = simulateBody
                    )
                }

                if (resultJson == null) {
                    showError("Simulation failed. Check Python server logs.")
                    return@launch
                }

                android.util.Log.d("SimulateFragment",
                    "Simulation result: ${resultJson.take(200)}")

                // Step 3: Parse result and store in ViewModel
                parseAndStoreSimulationResult(resultJson)

                // Step 4: Navigate to bottleneck screen
                (requireActivity() as SetupActivity)
                    .supportFragmentManager
                    .beginTransaction()
                    .replace(R.id.setup_container, BottleneckFragment())
                    .addToBackStack(null)
                    .commit()

            } catch (e: Exception) {
                android.util.Log.e("SimulateFragment", "Simulation error: ${e.message}")
                showError("Error: ${e.message}")
            } finally {
                binding.layoutLoading.visibility = View.GONE
                binding.btnExecuteSimulation.isEnabled = true
            }
        }
    }

    private fun buildSimulateRequestJson(): String {
        return """
        {
            "factory_type": "lathe",
            "demand": ${viewModel.demandUnits},
            "operators": ${viewModel.numWorkers},
            "shift_hours": ${viewModel.shiftHours},
            "machine_condition": "${viewModel.machineCondition}",
            "language": "en"
        }
        """.trimIndent()
    }

    private fun parseAndStoreSimulationResult(json: String) {
        try {
            val result = org.json.JSONObject(json)
            viewModel.lastSimulationResult = json
            viewModel.lastThroughput =
                result.optDouble("throughput_mean", 0.0).toFloat()
            val metrics = result.optJSONArray("station_metrics")
            if (metrics != null) {
                viewModel.lastStationMetrics = metrics.toString()
            }
            android.util.Log.d("SimulateFragment",
                "Parsed result: throughput=${viewModel.lastThroughput}")
        } catch (e: Exception) {
            android.util.Log.e("SimulateFragment", "Parse error: ${e.message}")
        }
    }

    private suspend fun postJson(
        url: String,
        json: String
    ): Boolean {
        return try {
            val client = okhttp3.OkHttpClient.Builder()
                .connectTimeout(10,
                    java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(30,
                    java.util.concurrent.TimeUnit.SECONDS)
                .build()
            val body = json.toRequestBody(
                "application/json".toMediaType()
            )
            val request = okhttp3.Request.Builder()
                .url(url)
                .post(body)
                .build()
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            Log.e("SimulateFragment",
                "POST failed to $url: ${e.message}")
            false
        }
    }

    private suspend fun postJsonAndGetResponse(
        url: String,
        json: String
    ): String? {
        return try {
            val client = okhttp3.OkHttpClient.Builder()
                .connectTimeout(10,
                    java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(60,
                    java.util.concurrent.TimeUnit.SECONDS)
                .build()
            val body = json.toRequestBody(
                "application/json".toMediaType()
            )
            val request = okhttp3.Request.Builder()
                .url(url)
                .post(body)
                .build()
            val response = client.newCall(request).execute()
            if (response.isSuccessful) response.body?.string()
            else null
        } catch (e: Exception) {
            Log.e("SimulateFragment",
                "POST failed to $url: ${e.message}")
            null
        }
    }

    private fun showError(message: String) {
        binding.layoutLoading.visibility = View.GONE
        binding.btnExecuteSimulation.isEnabled = true
        Toast.makeText(requireContext(), message, Toast.LENGTH_LONG).show()
    }

    private fun <T> selectChip(
        chips: List<Pair<android.view.View, T>>,
        defaultChip: android.view.View,
        defaultValue: T
    ) {
        chips.forEach { (c, _) ->
            c.setBackgroundResource(R.drawable.bg_chip_unselected)
            (c as? android.widget.TextView)?.setTextColor(resources.getColor(R.color.text_secondary, null))
        }
        defaultChip.setBackgroundResource(R.drawable.bg_chip_selected)
        (defaultChip as? android.widget.TextView)?.setTextColor(resources.getColor(R.color.primary, null))
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
