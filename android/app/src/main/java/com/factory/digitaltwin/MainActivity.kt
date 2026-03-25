package com.factory.digitaltwin

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.factory.digitaltwin.databinding.ActivityMainBinding
import com.factory.digitaltwin.ui.setup.FactorySetupActivity

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Force configured = true for testing
        getSharedPreferences("factory_prefs", MODE_PRIVATE)
            .edit().putBoolean("is_configured", true).apply()

        // Skip setup check for now — go straight to main
        setupNavigation()
    }

    private fun setupNavigation() {
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment)
                as NavHostFragment
        val navController = navHostFragment.navController
        binding.bottomNavigation
            .setupWithNavController(navController)
    }
}
