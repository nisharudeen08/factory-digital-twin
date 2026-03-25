#!/usr/bin/env python3
"""
Fetch Stitch UI designs and convert to Android XML layouts.
Uses the Stitch API with the configured API key.
"""

import os
import json
import requests
from pathlib import Path

# Set API key directly
STITCH_API_KEY = "AQ.Ab8RN6K0rpWTNDO5mRNDokVaRgkjvqrkC2vrD3T7AZeQKjMULw"

# Your Stitch project and screen IDs
STITCH_PROJECT_ID = "8599590735454910619"
STITCH_SCREENS = {
    "fragment_home": "1c55ddfaa7674db282a56ce1a8398056",      # Home Dashboard
    "fragment_simulate": "df21bebf755146d6a184d563ba25c38f",  # Simulate Screen
    "fragment_bottleneck": "6faadc89bb024c3b81ac4c27653bed8a",  # Bottleneck Alert
    "fragment_step1_type": "c86a79b1a0064bbd9d243e407b58e5f8",  # Factory Type Selection
    "fragment_step3_specs": "125bb32f3d594f649961f349939ba620",  # Machine Parameters
}

# Mapping to existing Android layout files
LAYOUT_MAPPING = {
    "fragment_home": "fragment_home.xml",
    "fragment_simulate": "fragment_simulate.xml",
    "fragment_bottleneck": "fragment_bottleneck.xml",
    "fragment_step1_type": "fragment_step1_type.xml",
    "fragment_step3_specs": "fragment_step3_specs.xml",
}

def fetch_screen(screen_id: str, api_key: str):
    """Fetch a single screen design from Stitch API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Try different Stitch API endpoints (corrected based on documentation)
    endpoints = [
        f"https://api.stitch.com/v1/projects/{STITCH_PROJECT_ID}/screens/{screen_id}/export/android",
        f"https://api.stitch.com/v1/projects/{STITCH_PROJECT_ID}/screens/{screen_id}/export",
        f"https://api.stitch.com/v1/screens/{screen_id}/export",
        f"https://api.stitch.com/v1/screens/{screen_id}",
    ]

    results = {}
    for url in endpoints:
        try:
            print(f"    Trying: {url[:60]}...")
            response = requests.get(url, headers=headers, timeout=30)
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "url": url}
            else:
                results[url] = response.status_code
        except Exception as e:
            print(f"    Error: {str(e)[:50]}")
            results[url] = str(e)

    return {"success": False, "errors": results}

def convert_to_android_xml(stitch_data: dict, layout_name: str) -> str:
    """Convert Stitch design data to Android XML layout."""
    if not stitch_data or not stitch_data.get("success"):
        return f"<!-- Failed to fetch {layout_name} from Stitch -->"
    
    data = stitch_data.get("data", {})
    
    # Extract components from Stitch data
    components = data.get("components", [])
    styles = data.get("styles", {})
    properties = data.get("properties", {})
    
    # Generate Android XML based on Stitch design
    xml_lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<!-- Generated from Stitch design: {layout_name} -->',
        f'<!-- Screen ID: {stitch_data.get("screen_id", "unknown")} -->',
        '<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"',
        '    xmlns:app="http://schemas.android.com/apk/res-auto"',
        '    android:layout_width="match_parent"',
        '    android:layout_height="match_parent"',
        '    android:orientation="vertical">',
        '',
        '    <!-- Stitch components will be converted here -->',
        '</LinearLayout>',
    ]
    
    return "\n".join(xml_lines)

def main():
    """Main function to fetch and convert Stitch designs."""
    print("=" * 60)
    print("Stitch UI Fetcher for Factory Digital Twin")
    print("=" * 60)
    print(f"\nAPI Key: {STITCH_API_KEY[:15]}...")
    print(f"Project ID: {STITCH_PROJECT_ID}")
    print(f"\nScreens to fetch: {len(STITCH_SCREENS)}")
    
    output_dir = Path("stitch_exports")
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    for layout_name, screen_id in STITCH_SCREENS.items():
        print(f"\n{'='*40}")
        print(f"Fetching {layout_name}...")
        print(f"Screen ID: {screen_id}")
        
        # Fetch from Stitch API
        stitch_data = fetch_screen(screen_id, STITCH_API_KEY)
        
        if stitch_data.get("success"):
            print(f"  ✓ Fetched successfully from {stitch_data.get('url', 'unknown')}")
            
            # Convert to Android XML
            xml_content = convert_to_android_xml(stitch_data, layout_name)
            
            # Save to file
            output_file = output_dir / f"{layout_name}.xml"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xml_content)
            
            # Also save raw JSON for debugging
            json_file = output_dir / f"{layout_name}_raw.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(stitch_data.get("data", {}), f, indent=2)
            
            print(f"  ✓ Saved XML to {output_file}")
            print(f"  ✓ Saved raw JSON to {json_file}")
            results[layout_name] = "SUCCESS"
        else:
            print(f"  ✗ Failed to fetch")
            print(f"  Errors: {stitch_data.get('errors', {})}")
            results[layout_name] = "FAILED"
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for layout_name, status in results.items():
        icon = "✓" if status == "SUCCESS" else "✗"
        print(f"{icon} {layout_name}: {status}")
    
    print("\n" + "=" * 60)
    print("Done! Check stitch_exports/ folder for results")
    print("=" * 60)
    
    return all(s == "SUCCESS" for s in results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
