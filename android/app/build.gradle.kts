plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.navigation.safeargs.kotlin")
    id("kotlin-parcelize")
}

// Unity streaming assets configuration
// The unityLibrary is at app/UnityExport/unityLibrary (where Unity 6 exports it).
var unityStreamingAssets: String = ""
val unityLibraryDir = file("${projectDir.absolutePath}/UnityExport/unityLibrary")
val manifestFile = file("${unityLibraryDir.absolutePath}/unityLibraryManifest.gradle")
if (manifestFile.exists()) {
    apply(from = manifestFile.absolutePath)
}

android {
    namespace = "com.factory.digitaltwin"
    compileSdk = 36
    ndkVersion = "27.2.12479018"

    defaultConfig {
        applicationId = "com.factory.digitaltwin"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        ndk {
            abiFilters.add("arm64-v8a")
            abiFilters.add("armeabi-v7a")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        viewBinding = true
        dataBinding = true
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
        resources {
            pickFirsts.add("**/libil2cpp.so")
            pickFirsts.add("**/libunity.so")
            pickFirsts.add("**/libmain.so")
            pickFirsts.add("**/libc++_shared.so")
        }
    }


    // Unity: Asset compression settings
    androidResources {
        noCompress += listOf(
            ".unity3d", ".ress",
            ".resource", ".obb",
            ".bundle", ".unityexp"
        )
        ignoreAssetsPattern =
            "!.svn:!.git:!.ds_store:" +
            "!*.scc:!CVS:!thumbs.db:" +
            "!picasa.ini:!*~"
    }
}

dependencies {
    // Core AndroidX
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.gridlayout:gridlayout:1.0.0")
    implementation("androidx.mediarouter:mediarouter:1.8.1")

    // Navigation
    val nav_version = "2.7.6"
    implementation("androidx.navigation:navigation-fragment-ktx:$nav_version")
    implementation("androidx.navigation:navigation-ui-ktx:$nav_version")

    // Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.java-websocket:Java-WebSocket:1.5.6")

    // Datastore
    implementation("androidx.datastore:datastore-preferences:1.0.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.8.7")



    // MPAndroidChart for history graphs
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

    // Unity Library — integrated for 3D view
    // NOTE: unity-classes.jar is exposed via 'api' in unityLibrary/build.gradle,
    // so it is transitively available here through the project dependency.
    // Do NOT add a separate fileTree here — that causes duplicate class errors.
    implementation("androidx.games:games-activity:3.0.5")
    implementation(project(":unityLibrary"))
    compileOnly(files("UnityExport/unityLibrary/libs/unity-classes.jar"))

    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
