pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }

        // Unity classes JAR lives inside the unityLibrary/libs folder.
        // This flatDir makes it visible to all modules (including :app).
        flatDir {
            dirs("app/UnityExport/unityLibrary/libs")
        }
    }
}
rootProject.name = "Factory Digital Twin"
include(":app")

// ── Unity Library ─────────────────────────────────────────────────────────────
// The Unity 6 export is placed inside android/app/UnityExport/unityLibrary.
// We always include it — the build will fail with a clear error if it is missing
// rather than silently omitting the module (which causes "Unresolved reference" errors).
include(":unityLibrary")
project(":unityLibrary").projectDir = File(settingsDir, "app/UnityExport/unityLibrary")
