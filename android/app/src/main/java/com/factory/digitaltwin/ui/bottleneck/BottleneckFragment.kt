package com.factory.digitaltwin.ui.bottleneck

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.factory.digitaltwin.databinding.FragmentBottleneckBinding
import com.factory.digitaltwin.viewmodel.SetupViewModel
import com.factory.digitaltwin.unity.UnityBridge

class BottleneckFragment : Fragment() {
    private var _binding: FragmentBottleneckBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SetupViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentBottleneckBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        
        // Hide button initially
        binding.btnView3d?.visibility = View.GONE

        loadBottleneckData()
        setupRecoverySteps()
    }

    private fun loadBottleneckData() {
        val metricsJson = viewModel.lastStationMetrics

        if (metricsJson.isEmpty()) {
            loadBottleneckDataFromEstimate()
            return
        }

        try {
            val metrics = org.json.JSONArray(metricsJson)
            var bottleneckStation: org.json.JSONObject? = null
            var highestBni = 0.0

            for (i in 0 until metrics.length()) {
                val station = metrics.getJSONObject(i)
                val bni = station.optDouble("bni", 0.0)
                val isBottleneck =
                    station.optBoolean("is_bottleneck", false)
                if (isBottleneck || bni > highestBni) {
                    highestBni = bni
                    bottleneckStation = station
                }
            }

            if (bottleneckStation == null &&
                metrics.length() > 0) {
                bottleneckStation = metrics.getJSONObject(0)
            }

            bottleneckStation?.let { s ->
                val stationName =
                    s.optString("station_name", "Unknown Station")
                val utilPct =
                    (s.optDouble("utilization", 0.0) * 100).toInt()
                val queue = s.optInt("queue_length", 0)
                val bni = s.optDouble("bni", 0.0)
                val dailyLoss =
                    s.optInt("daily_production_loss", 0)

                viewModel.lastBottleneckId =
                    s.optInt("station_id", -1)

                val selected = viewModel.getSelectedMachines()
                val stationTa = selected
                    .firstOrNull { it.nameEn == stationName }
                    ?.nameTa ?: ""

                binding.tvBottleneckStation.text = stationName
                binding.tvBottleneckStationTa.text = stationTa
                binding.tvUtilization.text = "$utilPct%"
                binding.progressUtilization.progress = utilPct
                binding.tvQueueCount.text =
                    if (queue > 0) "$queue jobs waiting in queue"
                    else "Queue clear"
                binding.tvDailyLoss.text =
                    if (dailyLoss > 0) "−$dailyLoss units/day"
                    else "On target"
                binding.tvBni.text =
                    "BNI: ${"%.2f".format(bni)}" +
                    when {
                        bni >= 0.85 -> " · Critical"
                        bni >= 0.70 -> " · Warning"
                        else        -> " · Normal"
                    }

                android.util.Log.d("BottleneckFragment",
                    "Bottleneck: $stationName" +
                    " util=$utilPct% bni=$bni loss=$dailyLoss")
            }
            
            // Step 1: ensure reveal button is called at end of try block
            revealView3DButton()

        } catch (e: Exception) {
            android.util.Log.e("BottleneckFragment", "Parse error: ${e.message}")
            loadBottleneckDataFromEstimate()
        }
    }

    private fun loadBottleneckDataFromEstimate() {
        val selected = viewModel.getSelectedMachines()
        if (selected.isEmpty()) return
        val bottleneck = selected.maxByOrNull {
            it.cycleTimeSec.toFloat() / it.count.toFloat()
        } ?: return
        binding.tvBottleneckStation.text = bottleneck.nameEn
        binding.tvBottleneckStationTa.text = bottleneck.nameTa
        binding.tvUtilization.text = "—"
        binding.tvBni.text = "Run simulation for real data"
        binding.tvDailyLoss.text = "—"
        binding.tvQueueCount.text = "No simulation data yet"
    }

    private fun setupRecoverySteps() {
        binding.btnStep1Done.setOnClickListener {
            it.isEnabled = false
            binding.btnStep2Done.isEnabled = true
            Toast.makeText(requireContext(), "Step 1 completed ✓", Toast.LENGTH_SHORT).show()
        }

        binding.btnStep2Done.setOnClickListener {
            it.isEnabled = false
            binding.btnStep3Done.isEnabled = true
            Toast.makeText(requireContext(), "Step 2 completed ✓", Toast.LENGTH_SHORT).show()
        }

        binding.btnStep3Done.setOnClickListener {
            it.isEnabled = false
            Toast.makeText(requireContext(), "All recovery steps completed! 🎉", Toast.LENGTH_LONG).show()
        }
    }

    private fun revealView3DButton() {
        // Evaluate initially just to decide whether to show the button
        val initialSelected = viewModel.getSelectedMachines()
        val total    = viewModel.getTotalMachines()

        if (initialSelected.isEmpty()) return

        binding.tvMachineSummary?.text =
            "$total machines configured"

        // Make button visible
        binding.btnView3d?.visibility = View.VISIBLE

        // Set click listener
        binding.btnView3d?.setOnClickListener {
            // Read fresh data NOW
            // not from a cached variable
            val machines = viewModel.getSelectedMachines()
            val demand  = viewModel.demandUnits
            val shift   = viewModel.shiftHours
            val workers = viewModel.numWorkers

            android.util.Log.d("BottleneckFragment",
                "getSelectedMachines returns: " +
                machines.map {
                    "${it.nameEn}×${it.count}"
                }.joinToString(", "))

            val stationJson =
                UnityBridge.buildStationResultsJson(
                    machines     = machines,
                    bottleneckId = viewModel.lastBottleneckId,
                    metricsJson  = viewModel.lastStationMetrics
                )
            UnityBridge.launch(
                context            = requireContext(),
                machines           = machines,
                demand             = demand,
                shift              = shift,
                workers            = workers,
                stationResultsJson = stationJson
            )
        }

        android.util.Log.d("BottleneckFragment",
            "3D button revealed for $total machines")
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
