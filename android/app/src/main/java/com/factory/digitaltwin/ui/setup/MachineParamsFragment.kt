package com.factory.digitaltwin.ui.setup

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.factory.digitaltwin.R
import com.factory.digitaltwin.SetupActivity
import com.factory.digitaltwin.databinding.FragmentMachineParamsBinding
import com.factory.digitaltwin.ui.simulate.SimulateFragment
import com.factory.digitaltwin.viewmodel.SetupViewModel

class MachineParamsFragment : Fragment() {
    private var _binding: FragmentMachineParamsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SetupViewModel by activityViewModels()
    private var selectedVariability = 0.08f

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMachineParamsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        loadCurrentMachine()
        setupVariabilityChips()
        setupNextButton()
    }

    private fun loadCurrentMachine() {
        val selected = viewModel.getSelectedMachines()
        val idx = viewModel.currentParamIndex
        if (idx >= selected.size) return
        
        val machine = selected[idx]
        val total = selected.size

        // Toolbar step label
        binding.tvParamsStep.text = "Step 2 of 3  ·  Machine ${idx + 1} of $total"

        // Footer progress label
        binding.tvParamsProgress.text = "Machine ${idx + 1} of $total — ${machine.nameEn}"

        // Machine identity
        binding.tvMachineEmoji.text = machine.emoji
        binding.tvMachineTitle.text = machine.nameEn
        binding.tvMachineTitleTa.text = machine.nameTa
        binding.tvMachineCountLabel.text =
            "${machine.count} machine" +
            "${if (machine.count != 1) "s" else ""}" +
            " in your factory"

        // Read-only count display
        binding.tvNumMachinesDisplay.text = machine.count.toString()

        // Pre-fill saved values
        binding.etCycleTime.setText(machine.cycleTimeSec.toString())
        binding.etMtbf.setText(machine.mtbfHours.toString())
        binding.etMttr.setText(machine.mttrHours.toString())
        binding.etSetupTime.setText(machine.setupMinutes.toString())

        // Progress bar
        val prog = ((idx + 1).toFloat() / total.toFloat() * 100).toInt()
        binding.progressParams.progress = prog

        // Update next button label
        if (idx == total - 1) {
            binding.btnParamsNext.text = "Go to Simulation →"
        } else {
            binding.btnParamsNext.text = "Save & Next Machine →"
        }
    }

    private fun setupVariabilityChips() {
        val chips = listOf(
            Pair(binding.chipVarLow,    0.08f),
            Pair(binding.chipVarMedium, 0.15f),
            Pair(binding.chipVarHigh,   0.25f)
        )
        chips.forEach { (chip, value) ->
            chip.setOnClickListener {
                selectedVariability = value
                chips.forEach { (c, _) ->
                    c.setBackgroundResource(R.drawable.bg_chip_unselected)
                    c.setTextColor(resources.getColor(R.color.text_secondary, null))
                }
                chip.setBackgroundResource(R.drawable.bg_chip_selected)
                chip.setTextColor(resources.getColor(R.color.primary, null))
            }
        }
    }

    private fun setupNextButton() {
        binding.btnParamsNext.setOnClickListener {
            saveCurrentMachine()
            val selected = viewModel.getSelectedMachines()
            val nextIdx = viewModel.currentParamIndex + 1

            if (nextIdx < selected.size) {
                // More machines to configure
                viewModel.currentParamIndex = nextIdx
                loadCurrentMachine()
                // Reset variability chip to low
                resetVariabilityChips()
            } else {
                // All machines done → Simulation screen
                (requireActivity() as SetupActivity)
                    .supportFragmentManager
                    .beginTransaction()
                    .replace(
                        R.id.setup_container,
                        SimulateFragment()
                    )
                    .addToBackStack(null)
                    .commit()
            }
        }
    }

    private fun resetVariabilityChips() {
        selectedVariability = 0.08f
        binding.chipVarLow.setBackgroundResource(R.drawable.bg_chip_selected)
        binding.chipVarLow.setTextColor(resources.getColor(R.color.primary, null))
        binding.chipVarMedium.setBackgroundResource(R.drawable.bg_chip_unselected)
        binding.chipVarMedium.setTextColor(resources.getColor(R.color.text_secondary, null))
        binding.chipVarHigh.setBackgroundResource(R.drawable.bg_chip_unselected)
        binding.chipVarHigh.setTextColor(resources.getColor(R.color.text_secondary, null))
    }

    private fun saveCurrentMachine() {
        val selected = viewModel.getSelectedMachines()
        val machine = selected[viewModel.currentParamIndex]

        machine.cycleTimeSec = binding.etCycleTime.text.toString().toIntOrNull() ?: 45
        machine.mtbfHours = binding.etMtbf.text.toString().toFloatOrNull() ?: 8.0f
        machine.mttrHours = binding.etMttr.text.toString().toFloatOrNull() ?: 0.5f
        machine.setupMinutes = binding.etSetupTime.text.toString().toIntOrNull() ?: 10
        machine.variability = selectedVariability
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
