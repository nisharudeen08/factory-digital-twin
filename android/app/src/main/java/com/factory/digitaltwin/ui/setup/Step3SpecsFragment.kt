package com.factory.digitaltwin.ui.setup

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.factory.digitaltwin.R
import com.factory.digitaltwin.databinding.FragmentStep3SpecsBinding

class Step3SpecsFragment : Fragment() {

    private var _binding:
        FragmentStep3SpecsBinding? = null
    private val binding get() = _binding!!

    private var machineCount = 2
    private var selectedVariability = "low"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentStep3SpecsBinding
            .inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        setupMachineStepper()
        setupVariabilityChips()
        setupNavButtons()
    }

    private fun setupMachineStepper() {
        binding.tvMachinesCount.text =
            machineCount.toString()

        binding.btnMachinesMinus.setOnClickListener {
            if (machineCount > 1) {
                machineCount--
                binding.tvMachinesCount.text =
                    machineCount.toString()
            }
        }

        binding.btnMachinesPlus.setOnClickListener {
            if (machineCount < 10) {
                machineCount++
                binding.tvMachinesCount.text =
                    machineCount.toString()
            }
        }
    }

    private fun setupVariabilityChips() {
        updateVariabilitySelection("low")

        binding.chipVariabilityLow.setOnClickListener {
            selectedVariability = "low"
            updateVariabilitySelection("low")
        }
        binding.chipVariabilityMedium
            .setOnClickListener {
            selectedVariability = "medium"
            updateVariabilitySelection("medium")
        }
        binding.chipVariabilityHigh.setOnClickListener {
            selectedVariability = "high"
            updateVariabilitySelection("high")
        }
    }

    private fun updateVariabilitySelection(
        selected: String
    ) {
        val selectedBg = R.drawable.bg_chip_selected
        val unselectedBg = R.drawable.bg_chip_unselected
        val selectedColor = R.color.primary
        val unselectedColor = R.color.text_secondary

        listOf(
            Pair(binding.chipVariabilityLow, "low"),
            Pair(binding.chipVariabilityMedium, "medium"),
            Pair(binding.chipVariabilityHigh, "high")
        ).forEach { (chip, type) ->
            if (type == selected) {
                chip.setBackgroundResource(selectedBg)
                chip.setTextColor(resources.getColor(
                    selectedColor, null))
            } else {
                chip.setBackgroundResource(unselectedBg)
                chip.setTextColor(resources.getColor(
                    unselectedColor, null))
            }
        }
    }

    private fun setupNavButtons() {
        binding.btnPrevious.setOnClickListener {
            requireActivity().onBackPressed()
        }

        binding.btnNext.setOnClickListener {
            saveCurrentMachineSpec()
            // TODO: navigate to next machine
            // or to review screen if last machine
        }
    }

    private fun saveCurrentMachineSpec() {
        val cycleTime = binding.etCycleTime
            .text.toString().toIntOrNull() ?: 45
        val mtbf = binding.etMtbf
            .text.toString().toFloatOrNull() ?: 8.0f
        val mttr = binding.etMttr
            .text.toString().toFloatOrNull() ?: 0.5f
        val variabilityFactor = when (selectedVariability) {
            "low"    -> 0.08f
            "medium" -> 0.15f
            "high"   -> 0.25f
            else     -> 0.15f
        }

        // Save to shared prefs
        val prefs = requireActivity()
            .getSharedPreferences(
                "factory_prefs",
                android.content.Context.MODE_PRIVATE)
        prefs.edit()
            .putInt("cycle_time", cycleTime)
            .putFloat("mtbf", mtbf)
            .putFloat("mttr", mttr)
            .putFloat("variability", variabilityFactor)
            .putInt("num_machines", machineCount)
            .apply()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
