package com.factory.digitaltwin.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.factory.digitaltwin.R
import com.factory.digitaltwin.databinding.FragmentWorkerDashboardBinding

class WorkerDashboardFragment : Fragment() {

    private var _binding:
        FragmentWorkerDashboardBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentWorkerDashboardBinding
            .inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        setupClickListeners()
        loadDashboardData()
    }

    private fun setupClickListeners() {
        // View 3D button → navigate to Unity tab
        binding.btnView3d.setOnClickListener {
            findNavController().navigate(
                R.id.nav_unity3d)
        }

        // Report issue button
        binding.btnReportIssue.setOnClickListener {
            // TODO: show report dialog
        }

        // 3D preview card → navigate to Unity tab
        binding.card3dPreview.setOnClickListener {
            findNavController().navigate(
                R.id.nav_unity3d)
        }
    }

    private fun loadDashboardData() {
        // Load from SharedViewModel when connected
        // For now show placeholder data
        binding.tvWorkerName.text = "Factory Worker"
        binding.tvShiftStatus.text = "Line 04 - Active"
        binding.tvActiveMachines.text = "14 / 15"
        binding.tvOutputRange.text = "160 - 210"
        binding.progressOutput.progress = 72
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
