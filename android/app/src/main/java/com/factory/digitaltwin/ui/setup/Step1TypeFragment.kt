package com.factory.digitaltwin.ui.setup

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.factory.digitaltwin.databinding.FragmentStep1TypeBinding

class Step1TypeFragment : Fragment() {

    private var _binding:
        FragmentStep1TypeBinding? = null
    private val binding get() = _binding!!

    private var selectedType = "lathe"
    private var stationCount = 4

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentStep1TypeBinding
            .inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)
        setupFactoryTypeCards()
        setupStationStepper()
        setupNextButton()
    }

    private fun setupFactoryTypeCards() {
        // Default: lathe selected
        updateCardSelection("lathe")

        binding.cardLathe.setOnClickListener {
            selectedType = "lathe"
            updateCardSelection("lathe")
        }
        binding.cardTextile.setOnClickListener {
            selectedType = "textile"
            updateCardSelection("textile")
        }
        binding.cardFood.setOnClickListener {
            selectedType = "food"
            updateCardSelection("food")
        }
        binding.cardElectronics.setOnClickListener {
            selectedType = "electronics"
            updateCardSelection("electronics")
        }
    }

    private fun updateCardSelection(selected: String) {
        // Reset all cards to unselected stroke
        listOf(
            binding.cardLathe,
            binding.cardTextile,
            binding.cardFood,
            binding.cardElectronics
        ).forEach { card ->
            card.strokeWidth = 2
            card.strokeColor =
                resources.getColor(
                    com.factory.digitaltwin.R.color.divider,
                    null)
        }

        // Highlight selected card
        val selectedCard = when (selected) {
            "lathe"       -> binding.cardLathe
            "textile"     -> binding.cardTextile
            "food"        -> binding.cardFood
            "electronics" -> binding.cardElectronics
            else          -> binding.cardLathe
        }
        selectedCard.strokeWidth = 4
        selectedCard.strokeColor =
            resources.getColor(
                com.factory.digitaltwin.R.color.primary,
                null)
    }

    private fun setupStationStepper() {
        binding.tvStationCount.text =
            stationCount.toString()

        binding.btnStationsMinus.setOnClickListener {
            if (stationCount > 1) {
                stationCount--
                binding.tvStationCount.text =
                    stationCount.toString()
            }
        }

        binding.btnStationsPlus.setOnClickListener {
            if (stationCount < 12) {
                stationCount++
                binding.tvStationCount.text =
                    stationCount.toString()
            }
        }
    }

    private fun setupNextButton() {
        binding.btnNext.setOnClickListener {
            // Save to shared prefs for now
            val prefs = requireActivity()
                .getSharedPreferences(
                    "factory_prefs",
                    android.content.Context.MODE_PRIVATE)
            prefs.edit()
                .putString("factory_type", selectedType)
                .putInt("station_count", stationCount)
                .apply()

            // Navigate to step 2
            // TODO: add step 2 fragment navigation
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
