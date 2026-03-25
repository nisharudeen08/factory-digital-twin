package com.factory.digitaltwin

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import com.factory.digitaltwin.model.MachineConfig
import com.factory.digitaltwin.unity.UnityBridge

class WelcomeActivity : AppCompatActivity() {
    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        findViewById<Button>(R.id.btn_start_setup)
            .setOnClickListener {
                startActivity(
                    Intent(this,
                        SetupActivity::class.java)
                )
            }

        // findViewById<Button>(R.id.btn_test_unity)
        //    .setOnClickListener {
        //        launchUnityTest()
        //    }
    }

    private fun launchUnityTest() {
        val testMachines = listOf(
            MachineConfig(
                id = "lathe",
                nameEn = "Lathe Machine",
                nameTa = "தட்டு இயந்திரம்",
                emoji = "⚙️",
                count = 2,
                cycleTimeSec = 45,
                mtbfHours = 8.0f,
                mttrHours = 0.5f,
                setupMinutes = 10,
                variability = 0.15f
            ),
            MachineConfig(
                id = "cnc",
                nameEn = "CNC Milling",
                nameTa = "சி.என்.சி.",
                emoji = "🔧",
                count = 1,
                cycleTimeSec = 60,
                mtbfHours = 12.0f,
                mttrHours = 0.5f,
                setupMinutes = 15,
                variability = 0.15f
            ),
            MachineConfig(
                id = "weld",
                nameEn = "Welding Station",
                nameTa = "வெல்டிங்",
                emoji = "🔥",
                count = 1,
                cycleTimeSec = 55,
                mtbfHours = 6.0f,
                mttrHours = 0.8f,
                setupMinutes = 12,
                variability = 0.15f
            ),
            MachineConfig(
                id = "band_saw",
                nameEn = "Band Saw",
                nameTa = "பேண்ட் சா",
                emoji = "🪚",
                count = 1,
                cycleTimeSec = 35,
                mtbfHours = 10.0f,
                mttrHours = 0.3f,
                setupMinutes = 6,
                variability = 0.15f
            )
        )
        UnityBridge.launch(
            context  = this,
            machines = testMachines,
            demand   = 200,
            shift    = 8f,
            workers  = 2
        )
    }
}
