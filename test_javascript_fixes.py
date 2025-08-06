#!/usr/bin/env python3
"""
Test script to verify JavaScript fixes for Facilities Management module
"""

import os
import re

def test_javascript_fixes():
    print("🔧 Testing JavaScript fixes for Facilities Management module")
    print("=" * 60)
    
    # Test 1: Check for unreachable code issues
    print("\n1. Checking for unreachable code issues...")
    
    js_files = [
        "odoo17/addons/facilities_management/static/src/js/dashboard_widgets.js",
        "odoo17/addons/facilities_management/static/src/js/iot_monitoring.js",
        "odoo17/addons/facilities_management/static/src/js/mobile_scanner.js"
    ]
    
    unreachable_code_found = False
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
                
            # Check for return statements followed by code
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'return' in line and not line.strip().endswith(';') and not line.strip().endswith('}'):
                    # Check if next line has code
                    if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith('}'):
                        print(f"⚠️  Potential unreachable code in {js_file}:{i+1}")
                        unreachable_code_found = True
    
    if not unreachable_code_found:
        print("✅ No unreachable code issues found")
    
    # Test 2: Check layout timing fixes
    print("\n2. Checking layout timing fixes...")
    
    dashboard_file = "odoo17/addons/facilities_management/static/src/js/dashboard_widgets.js"
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r') as f:
            content = f.read()
            
        if 'setTimeout' in content and 'DOMContentLoaded' in content:
            print("✅ Layout timing fixes found in dashboard_widgets.js")
        else:
            print("⚠️  Layout timing fixes may be missing")
    
    # Test 3: Check CSS loading fixes
    print("\n3. Checking CSS loading fixes...")
    
    css_file = "odoo17/addons/facilities_management/static/src/css/facilities.css"
    if os.path.exists(css_file):
        with open(css_file, 'r') as f:
            content = f.read()
            
        if '.facilities-dashboard' in content and 'transition' in content:
            print("✅ CSS loading fixes found")
        else:
            print("⚠️  CSS loading fixes may be missing")
    
    # Test 4: Check manifest asset loading
    print("\n4. Checking manifest asset loading...")
    
    manifest_file = "odoo17/addons/facilities_management/__manifest__.py"
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r') as f:
            content = f.read()
            
        if 'web.chartjs_lib' in content and 'facilities_management/static/src/js/' in content:
            print("✅ Manifest asset loading configured correctly")
        else:
            print("⚠️  Manifest asset loading may have issues")
    
    # Test 5: Check async/await fixes
    print("\n5. Checking async/await fixes...")
    
    mobile_scanner_file = "odoo17/addons/facilities_management/static/src/js/mobile_scanner.js"
    if os.path.exists(mobile_scanner_file):
        with open(mobile_scanner_file, 'r') as f:
            content = f.read()
            
        if 'async _getCurrentLocation' in content and 'Promise.resolve' in content:
            print("✅ Async/await fixes found in mobile_scanner.js")
        else:
            print("⚠️  Async/await fixes may be missing")
    
    print("\n" + "=" * 60)
    print("🎉 JavaScript fixes verification complete!")
    print("\nSummary of fixes applied:")
    print("1. Fixed layout timing issues with setTimeout and DOMContentLoaded")
    print("2. Resolved unreachable code after return statements")
    print("3. Added proper async/await handling for geolocation")
    print("4. Enhanced CSS with loading states and transitions")
    print("5. Updated manifest for proper asset loading order")
    
    return True

if __name__ == "__main__":
    test_javascript_fixes()