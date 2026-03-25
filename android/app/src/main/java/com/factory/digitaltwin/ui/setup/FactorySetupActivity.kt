package com.factory.digitaltwin.ui.setup

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.factory.digitaltwin.MainActivity
import com.factory.digitaltwin.R
import com.factory.digitaltwin.databinding.ActivityFactorySetupBinding

class FactorySetupActivity : AppCompatActivity() {

    private lateinit var binding:
        ActivityFactorySetupBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFactorySetupBinding
            .inflate(layoutInflater)
        setContentView(binding.root)
    }

    // Called when setup is complete
    fun onSetupComplete() {
        val prefs = getSharedPreferences(
            "factory_prefs", MODE_PRIVATE)
        prefs.edit().putBoolean(
            "is_configured", true).apply()
        startActivity(Intent(
            this, MainActivity::class.java))
        finish()
    }
}
