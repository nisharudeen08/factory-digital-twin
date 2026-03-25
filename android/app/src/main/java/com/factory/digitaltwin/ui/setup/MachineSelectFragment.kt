package com.factory.digitaltwin.ui.setup

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.factory.digitaltwin.R
import com.factory.digitaltwin.SetupActivity
import com.factory.digitaltwin.databinding.FragmentMachineSelectBinding
import com.factory.digitaltwin.viewmodel.SetupViewModel

class MachineSelectFragment : Fragment() {
    private var _binding: FragmentMachineSelectBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SetupViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMachineSelectBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        setupSteppers()
        setupNextButton()
        updateTotal()
    }

    private data class MachineControl(
        val id: String,
        val minus: View,
        val countView: android.widget.TextView,
        val plus: View
    )

    private fun setupSteppers() {
        val controls = listOf(
            MachineControl("lathe", binding.btnLatheMinus, binding.tvLatheCount, binding.btnLathePlus),
            MachineControl("cnc", binding.btnCncMinus, binding.tvCncCount, binding.btnCncPlus),
            MachineControl("drill", binding.btnDrillMinus, binding.tvDrillCount, binding.btnDrillPlus),
            MachineControl("weld", binding.btnWeldMinus, binding.tvWeldCount, binding.btnWeldPlus),
            MachineControl("grind", binding.btnGrindMinus, binding.tvGrindCount, binding.btnGrindPlus),
            MachineControl("band_saw", binding.btnBandsawMinus, binding.tvBandsawCount, binding.btnBandsawPlus),
            MachineControl("qc", binding.btnQcMinus, binding.tvQcCount, binding.btnQcPlus)
        )

        controls.forEach { (id, minus, countView, plus) ->
            val machine = viewModel.availableMachines.first { it.id == id }

            countView.text = machine.count.toString()

            minus.setOnClickListener {
                if (machine.count > 0) {
                    machine.count--
                    countView.text = machine.count.toString()
                    updateTotal()
                }
            }

            plus.setOnClickListener {
                if (machine.count < 10) {
                    machine.count++
                    countView.text = machine.count.toString()
                    updateTotal()
                }
            }
        }
    }

    private fun setupNextButton() {
        binding.btnNextToParams.setOnClickListener {
            if (viewModel.getTotalMachines() == 0) {
                Toast.makeText(
                    requireContext(),
                    "Please add at least 1 machine",
                    Toast.LENGTH_SHORT
                ).show()
                return@setOnClickListener
            }
            viewModel.currentParamIndex = 0
            (requireActivity() as SetupActivity)
                .supportFragmentManager
                .beginTransaction()
                .replace(
                    R.id.setup_container,
                    MachineParamsFragment()
                )
                .addToBackStack(null)
                .commit()
        }
    }

    private fun updateTotal() {
        val total = viewModel.getTotalMachines()
        val types = viewModel.getTotalStationTypes()
        binding.tvTotalMachines.text =
            "$total machine${if (total != 1) "s" else ""}" +
            " · $types type${if (types != 1) "s" else ""}"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
