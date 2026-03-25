# Stitch UI Integration Guide

## Project Info
- **Stitch Project ID**: `8599590735454910619`
- **Project Title**: Factory Digital Twin UI

## Screen Mapping

Your Stitch screens map to these Android layout files:

| # | Stitch Screen | Screen ID | Android Layout File | Fragment |
|---|---------------|-----------|---------------------|----------|
| 1 | Setup: Machine Parameters | `125bb32f3d594f649961f349939ba620` | `fragment_step3_specs.xml` | `Step3SpecsFragment.kt` |
| 2 | Home Dashboard | `1c55ddfaa7674db282a56ce1a8398056` | `fragment_home.xml` | `HomeFragment.kt` |
| 3 | Bottleneck Alert | `6faadc89bb024c3b81ac4c27653bed8a` | `fragment_bottleneck.xml` | `BottleneckFragment.kt` |
| 4 | Factory Type Selection | `c86a79b1a0064bbd9d243e407b58e5f8` | `fragment_step1_type.xml` | `Step1TypeFragment.kt` |
| 5 | Simulate Screen | `df21bebf755146d6a184d563ba25c38f` | `fragment_simulate.xml` | `SimulateFragment.kt` |

## How to Export from Stitch

### Method 1: Manual Export (Recommended)

1. **Open Stitch** and navigate to your project
2. **Select each screen** and click the **Export** button
3. **Choose format**:
   - For images/mockups: PNG or JPG
   - For code: Android XML
4. **Save to folder**: `stitch_exports/`

### Method 2: API Export

```bash
# Set your API key
export STITCH_API_KEY="your_api_key_here"

# Project ID
PROJECT_ID="8599590735454910619"

# Export each screen (replace URLs with actual Stitch API endpoints)
curl -L -H "Authorization: Bearer $STITCH_API_KEY" \
  -o "stitch_exports/setup_machine_params.png" \
  "https://api.stitch.com/v1/projects/$PROJECT_ID/screens/125bb32f3d594f649961f349939ba620/export.png"

# ... repeat for other screens
```

### Method 3: Stitch CLI (if available)

```bash
stitch export --project 8599590735454910619 --output ./stitch_exports
```

## How to Import into Android

### Step 1: Export Assets from Stitch

Export the following from Stitch:
- [ ] Images/icons (PNG)
- [ ] Color values (XML or JSON)
- [ ] String resources (XML or JSON)
- [ ] Layout XML (if using Stitch code generation)

### Step 2: Add Images to Android

```
android/app/src/main/res/
├── drawable/          # For images used in layouts
├── drawable-hdpi/     # Medium density screens
├── drawable-xhdpi/    # High density screens
├── drawable-xxhdpi/   # Extra high density
└── mipmap-*/          # App icons
```

Copy your Stitch images to appropriate folders:
```bash
copy stitch_exports\*.png android\app\src\main\res\drawable-xxhdpi\
```

### Step 3: Update Colors (if needed)

Edit `android/app/src/main/res/values/colors.xml`:

```xml
<resources>
    <!-- Add your Stitch colors here -->
    <color name="stitch_primary">#FF6200EE</color>
    <color name="stitch_secondary">#FF03DAC5</color>
    <color name="stitch_background">#FFFFFFFF</color>
</resources>
```

### Step 4: Update Strings (if needed)

Edit `android/app/src/main/res/values/strings.xml`:

```xml
<resources>
    <!-- Add your Stitch strings here -->
    <string name="setup_title">Machine Parameters</string>
    <string name="home_dashboard">Dashboard</string>
    <string name="bottleneck_alert">Bottleneck Detected!</string>
</resources>
```

### Step 5: Update Layouts

Your existing layouts are already in place. To update them with Stitch designs:

1. **If Stitch generated XML**: Copy the generated XML and merge with existing layouts
2. **If Stitch is images only**: Use images as reference to modify existing layouts

Example - Update `fragment_simulate.xml`:
```xml
<!-- Existing layout - keep structure -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Update styles to match Stitch design -->
    <TextView
        android:id="@+id/tvDemand"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="@dimen/stitch_title_size"
        android:textColor="@color/stitch_primary_text"
        android:fontFamily="@font/stitch_font" />

</LinearLayout>
```

## Quick Integration Script

Run this to set up the folder structure:

```bash
# Create export folder
mkdir stitch_exports

# Copy reference images to Android
mkdir android\app\src\main\res\drawable-xxhdpi\stitch_refs
copy stitch_exports\*.png android\app\src\main\res\drawable-xxhdpi\stitch_refs\

# Create backup of current layouts
mkdir backup_layouts
copy android\app\src\main\res\layout\*.xml backup_layouts\
```

## Verification Checklist

After integration, verify:

- [ ] All 5 Stitch screens are visible in Android app
- [ ] Colors match Stitch design
- [ ] Fonts and text sizes match
- [ ] Button styles match
- [ ] Layout spacing/margins match
- [ ] Images/icons display correctly
- [ ] Navigation between screens works
- [ ] App builds without errors

## Testing

```bash
cd android
./gradlew assembleDebug
# Install on device/emulator and verify UI matches Stitch
```

## Troubleshooting

### Images not showing
- Check image file names are lowercase (Android requirement)
- Verify images are in correct `drawable-` folder
- Clean and rebuild: `Build > Clean Project > Rebuild Project`

### Colors wrong
- Check color hex values in `colors.xml`
- Verify you're referencing the correct color resource

### Layout broken
- Compare with Stitch export preview
- Check constraint/linear layout parameters
- Use Android Studio's Layout Inspector

## Need Help?

1. Open Stitch and take screenshots of each screen
2. Compare side-by-side with Android app
3. Note differences and update layouts accordingly
4. Use Android Studio's Preview mode to see changes in real-time
