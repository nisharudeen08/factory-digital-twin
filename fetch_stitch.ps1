# Stitch Asset Fetcher
# Fetches images and code from Stitch for Factory Digital Twin project

param(
    [string]$ApiKey = "",
    [string]$ProjectId = "8599590735454910619",
    [string]$OutputDir = "stitch_exports"
)

# Screen IDs from your Stitch project
$Screens = @{
    "setup_machine_params" = "125bb32f3d594f649961f349939ba620"
    "home_dashboard" = "1c55ddfaa7674db282a56ce1a8398056"
    "bottleneck_alert" = "6faadc89bb024c3b81ac4c27653bed8a"
    "factory_type" = "c86a79b1a0064bbd9d243e407b58e5f8"
    "simulate_screen" = "df21bebf755146d6a184d563ba25c38f"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stitch Asset Fetcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project ID: $ProjectId" -ForegroundColor Yellow
Write-Host ""

# Check for API key
if ([string]::IsNullOrEmpty($ApiKey)) {
    Write-Host "ERROR: API Key not provided!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please provide your Stitch API key in one of these ways:" -ForegroundColor Yellow
    Write-Host "  1. Set environment variable: `$env:STITCH_API_KEY = 'your_key_here'" -ForegroundColor White
    Write-Host "  2. Run script with parameter: .\fetch_stitch.ps1 -ApiKey 'your_key_here'" -ForegroundColor White
    Write-Host ""
    Write-Host "To get your API key:" -ForegroundColor Yellow
    Write-Host "  1. Open Stitch" -ForegroundColor White
    Write-Host "  2. Go to Settings > API" -ForegroundColor White
    Write-Host "  3. Copy your API key" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "Created output directory: $OutputDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "Screens to fetch:" -ForegroundColor Cyan
foreach ($screen in $Screens.GetEnumerator()) {
    Write-Host "  - $($screen.Key): $($screen.Value)" -ForegroundColor White
}
Write-Host ""

# Stitch API base URL (adjust if different)
$StitchApiBase = "https://api.stitch.com/v1"
$Headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}

# Try to fetch each screen
foreach ($screen in $Screens.GetEnumerator()) {
    $screenName = $screen.Key
    $screenId = $screen.Value
    
    Write-Host "Fetching: $screenName..." -NoNewline
    
    # Try different export formats
    $exportUrls = @(
        "$StitchApiBase/projects/$ProjectId/screens/$screenId/export.png",
        "$StitchApiBase/projects/$ProjectId/screens/$screenId/export.xml",
        "$StitchApiBase/projects/$ProjectId/screens/$screenId/assets"
    )
    
    $fetched = $false
    foreach ($url in $exportUrls) {
        try {
            $outputPath = Join-Path $OutputDir "$screenName.png"
            Invoke-RestMethod -Uri $url -Headers $Headers -OutFile $outputPath -ErrorAction Stop
            Write-Host " ✓ Downloaded: $outputPath" -ForegroundColor Green
            $fetched = $true
            break
        } catch {
            # Try next URL
            continue
        }
    }
    
    if (-not $fetched) {
        Write-Host " ✗ Failed (check API key and screen ID)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check the '$OutputDir' folder for exported assets." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review exported images in $OutputDir" -ForegroundColor White
Write-Host "  2. Copy images to: android\app\src\main\res\drawable-xxhdpi\" -ForegroundColor White
Write-Host "  3. Update layouts to match Stitch design" -ForegroundColor White
Write-Host "  4. Build and test Android app" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
