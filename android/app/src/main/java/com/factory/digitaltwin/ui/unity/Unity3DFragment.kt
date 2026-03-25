package com.factory.digitaltwin.ui.unity

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import com.factory.digitaltwin.databinding.FragmentUnity3dBinding
import com.unity3d.player.IUnityPlayerLifecycleEvents
import com.unity3d.player.UnityPlayerForGameActivity
import android.view.SurfaceView

import androidx.fragment.app.activityViewModels
import com.factory.digitaltwin.viewmodel.SetupViewModel
import com.unity3d.player.UnityPlayer

class Unity3DFragment : Fragment(), IUnityPlayerLifecycleEvents {

    private var _binding: FragmentUnity3dBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: SetupViewModel by activityViewModels()
    private var unityPlayer: UnityPlayerForGameActivity? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentUnity3dBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Use a SurfaceView as expected by Unity Player
        val surfaceView = SurfaceView(requireContext())
        
        // Initialize Unity Player
        try {
            val frameLayout = binding.unityContainer
            
            unityPlayer = UnityPlayerForGameActivity(requireActivity(), frameLayout, surfaceView, this)
            
            unityPlayer?.onStart()
            unityPlayer?.onResume()
            
            // Hide loading text after a delay
            view.postDelayed({
                binding.loadingText.visibility = View.GONE
                sendDataToUnity()
            }, 3000)
            
        } catch (e: Exception) {
            e.printStackTrace()
            binding.loadingText.text = "Error starting 3D: ${e.message}"
        }
    }

    /**
     * Send current simulation results and configuration to Unity
     */
    private fun sendDataToUnity() {
        try {
            val json = viewModel.getUnitySimulationJson()
            android.util.Log.d("Unity3DFragment", "Sending to Unity: $json")
            
            // Format: UnitySendMessage("StationaryName", "MethodName", "Message")
            UnityPlayer.UnitySendMessage("simulation manager", "ReceiveStationData", json)
            
            // Also set language
            // SimulationManager has SetLanguage(string lang)
            // Need to know current lang - default to "en"
            UnityPlayer.UnitySendMessage("simulation manager", "SetLanguage", "en")
            
        } catch (e: Exception) {
            android.util.Log.e("Unity3DFragment", "Error sending data: ${e.message}")
        }
    }

    override fun onResume() {
        super.onResume()
        unityPlayer?.onResume()
        // Resend data on resume to ensure Unity is up to date
        view?.postDelayed({ sendDataToUnity() }, 500)
    }

    override fun onPause() {
        super.onPause()
        unityPlayer?.onPause()
    }

    override fun onStart() {
        super.onStart()
        unityPlayer?.onStart()
    }

    override fun onStop() {
        super.onStop()
        unityPlayer?.onStop()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // unityPlayer?.destroy() // Usually UnityPlayer is kept alive until app close
        _binding = null
    }

    // IUnityPlayerLifecycleEvents implementation
    override fun onUnityPlayerUnloaded() {
        // Handle Unity unloading
    }

    override fun onUnityPlayerQuitted() {
        // Handle Unity quitting
    }
}
