package com.factory.digitaltwin.ui.unity

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.WindowManager
import com.unity3d.player.UnityPlayer
import com.unity3d.player.UnityPlayerGameActivity

class Unity3DActivity : UnityPlayerGameActivity() {

    companion object {
        private const val TAG = "Unity3DActivity"
        const val EXTRA_CONFIG_JSON  = "config_json"
        const val EXTRA_STATION_DATA = "station_data"

        // UnitySendMessage is CASE-SENSITIVE.
        // We try all known casing variants to handle
        // any mismatch between Android and Unity scene.
        private val UNITY_GAME_OBJECTS = listOf(
            "simulation manager",   // original lowercase
            "Simulation Manager",   // title case
            "SimulationManager",    // no space
            "SimManager"            // short form
        )

        private const val UNITY_METHOD_CONFIG   = "ReceiveConfigFromAndroid"
        private const val UNITY_METHOD_STATION  = "ReceiveStationData"
        private const val UNITY_METHOD_LANGUAGE = "SetLanguage"
        private const val UNITY_METHOD_IP       = "SetPythonServerIP"
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private var configAlreadySent = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val cfg = intent.getStringExtra(EXTRA_CONFIG_JSON)
        Log.d(TAG, "=== Unity3DActivity started ===")
        Log.d(TAG, "Config: " + when {
            cfg.isNullOrEmpty() -> "MISSING — Unity will be empty"
            else                -> "OK length=${cfg.length} chars"
        })

        // Attempt 1 — at 2 s (Unity usually ready by now)
        mainHandler.postDelayed({
            Log.d(TAG, "--- Attempt 1 at 2 s ---")
            sendConfigToUnity()
        }, 2000L)

        // Attempt 2 — at 4 s (safety net for slow devices)
        mainHandler.postDelayed({
            if (!configAlreadySent) {
                Log.d(TAG, "--- Attempt 2 at 4 s (config not yet confirmed) ---")
                sendConfigToUnity()
            } else {
                Log.d(TAG, "--- Attempt 2 at 4 s skipped (already sent) ---")
            }
        }, 4000L)

        // Attempt 3 — at 7 s (final safety net)
        mainHandler.postDelayed({
            if (!configAlreadySent) {
                Log.d(TAG, "--- Attempt 3 at 7 s (config not yet confirmed) ---")
                sendConfigToUnity()
            } else {
                Log.d(TAG, "--- Attempt 3 at 7 s skipped (already sent) ---")
            }
        }, 7000L)

        addBackButton()
    }

    // ──────────────────────────────────────────────────────────────
    // Send all data to Unity
    // ──────────────────────────────────────────────────────────────

    // Add floating back button over Unity view
    private fun addBackButton() {
        val backBtn = android.widget.ImageButton(this)
        backBtn.setImageResource(
            android.R.drawable.ic_menu_close_clear_cancel)
        backBtn.setBackgroundColor(
            android.graphics.Color.parseColor("#CC000000"))
        backBtn.setPadding(24, 24, 24, 24)

        val params = android.widget.FrameLayout.LayoutParams(
            120, 120
        ).apply {
            gravity = android.view.Gravity.TOP or
                      android.view.Gravity.START
            topMargin  = 48
            leftMargin = 48
        }

        backBtn.setOnClickListener {
            finish()
        }

        // Add to window decorView
        val decorView = window.decorView as
            android.widget.FrameLayout
        decorView.addView(backBtn, params)
    }

    private fun sendConfigToUnity() {
        try {
            val configJson = intent.getStringExtra(EXTRA_CONFIG_JSON)

            if (configJson.isNullOrEmpty()) {
                Log.w(TAG, "sendConfigToUnity: no config JSON in Intent — aborting.")
                return
            }

            Log.d(TAG, "sendConfigToUnity: json length=${configJson.length}")

            // STEP 0 — Send server IP first (for WebSocket / Flow 2)
            val serverIp = try {
                com.factory.digitaltwin.ui.simulate.SimulateFragment.PYTHON_SERVER_URL
                    .removePrefix("http://")
                    .removePrefix("https://")
                    .split(":")[0]
                    .trim()
            } catch (e: Exception) {
                Log.w(TAG, "Could not read PYTHON_SERVER_URL: ${e.message}")
                ""
            }

            if (serverIp.isNotEmpty()) {
                Log.d(TAG, "Sending server IP to Unity: $serverIp")
                sendToAllObjects(UNITY_METHOD_IP, serverIp, logSuccess = true)
            }

            // STEP 1 — Send config JSON (Flow 1 — machine spawning)
            Log.d(TAG, "Sending config to Unity (${configJson.length} chars)...")
            val sent = sendToAllObjects(UNITY_METHOD_CONFIG, configJson, logSuccess = true)
            if (sent) configAlreadySent = true

            // STEP 2 — Send language preference
            val lang = getSharedPreferences("factory_prefs", MODE_PRIVATE)
                .getString("language", "en") ?: "en"
            sendToAllObjects(UNITY_METHOD_LANGUAGE, lang, logSuccess = false)
            Log.d(TAG, "Language sent: $lang")

            // STEP 3 — Send station data if available (Flow 2 pre-loaded results)
            val stationData = intent.getStringExtra(EXTRA_STATION_DATA)
            if (!stationData.isNullOrEmpty()) {
                Log.d(TAG, "Station data available (${stationData.length} chars) — sending after 2 s delay")
                mainHandler.postDelayed({
                    sendToAllObjects(UNITY_METHOD_STATION, stationData, logSuccess = true)
                    Log.d(TAG, "Station data sent.")
                }, 2000L)
            }

            Log.d(TAG, "sendConfigToUnity: complete.")

        } catch (e: Exception) {
            Log.e(TAG, "sendConfigToUnity error: ${e.message}", e)
        }
    }

    /**
     * Sends a UnitySendMessage to ALL known GameObject name variants.
     * UnitySendMessage does NOT throw if the object is not found —
     * it silently fails. We log each attempt so Logcat shows which
     * name actually worked (i.e. which one Unity received).
     *
     * @return true if at least one call was made without exception.
     */
    private fun sendToAllObjects(
        method: String,
        message: String,
        logSuccess: Boolean
    ): Boolean {
        var anySucceeded = false
        for (objName in UNITY_GAME_OBJECTS) {
            try {
                UnityPlayer.UnitySendMessage(objName, method, message)
                if (logSuccess) {
                    Log.d(TAG, "UnitySendMessage → '$objName'.$method (${message.length} chars)")
                }
                anySucceeded = true
            } catch (e: Exception) {
                Log.w(TAG, "UnitySendMessage → '$objName'.$method FAILED: ${e.message}")
            }
        }
        return anySucceeded
    }

    override fun onBackPressed() {
        finish()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        // Required by Unity for correct rendering lifecycle
    }
}
