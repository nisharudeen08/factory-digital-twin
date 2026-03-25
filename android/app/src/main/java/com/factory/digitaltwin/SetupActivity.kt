package com.factory.digitaltwin

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.factory.digitaltwin.ui.setup.MachineSelectFragment
import com.factory.digitaltwin.viewmodel.SetupViewModel

class SetupActivity : AppCompatActivity() {
    val viewModel: SetupViewModel by viewModels()

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_setup)

        if (savedInstanceState == null) {
            supportFragmentManager
                .beginTransaction()
                .replace(
                    R.id.setup_container,
                    MachineSelectFragment()
                )
            .commit()
        }
    }
}
