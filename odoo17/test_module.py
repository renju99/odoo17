#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    # Try to import the module
    from addons.facilities_management import __manifest__
    print("✅ Module manifest loaded successfully")
    print(f"Module name: {__manifest__.get('name', 'Unknown')}")
    print(f"Module version: {__manifest__.get('version', 'Unknown')}")
    print(f"Dependencies: {__manifest__.get('depends', [])}")
    
    # Check if assets are properly defined
    assets = __manifest__.get('assets', {})
    if 'web.assets_backend' in assets:
        print("✅ Backend assets defined")
        for asset in assets['web.assets_backend']:
            if 'mobile_workorders_enhanced_action.js' in asset:
                print(f"✅ Found mobile_workorders_enhanced_action.js: {asset}")
    else:
        print("❌ No backend assets defined")
        
except ImportError as e:
    print(f"❌ Failed to import module: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nChecking if JavaScript files exist:")
js_files = [
    'addons/facilities_management/static/src/js/mobile_workorder.js',
    'addons/facilities_management/static/src/js/mobile_workorders_enhanced_action.js',
    'addons/facilities_management/static/src/xml/mobile_workorders_enhanced.xml'
]

for js_file in js_files:
    if os.path.exists(js_file):
        print(f"✅ {js_file}")
    else:
        print(f"❌ {js_file} - NOT FOUND") 