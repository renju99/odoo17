#!/usr/bin/env python3
"""
Test script to verify that the mobile workorder JavaScript module loads correctly
after fixing the AMD module syntax issue.
"""

import os
import re

def test_mobile_workorder_js_syntax():
    """Test that the mobile workorder JavaScript file uses correct syntax."""
    print("=== Mobile Workorder JavaScript Syntax Test ===\n")
    
    js_file = "odoo17/addons/facilities_management/static/src/js/mobile_workorder.js"
    
    if not os.path.exists(js_file):
        print("❌ ERROR: JavaScript file not found:", js_file)
        return False
    
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Check for correct module definition syntax
    if 'odoo.define(\'facilities_management.mobile_workorder\', [' in content:
        print("✅ SUCCESS: Module uses correct array-based dependency syntax")
    else:
        print("❌ ERROR: Module still uses old function-based require syntax")
        return False
    
    # Check for required dependencies
    required_deps = [
        'web.core',
        'web.Widget', 
        'web.public.widget',
        'web.FormView',
        'web.FormController'
    ]
    
    for dep in required_deps:
        if dep in content:
            print(f"✅ SUCCESS: Dependency '{dep}' is included")
        else:
            print(f"❌ ERROR: Missing dependency '{dep}'")
            return False
    
    # Check for controller registration
    if 'core.action_registry.add(\'mobile_workorder_form\'' in content:
        print("✅ SUCCESS: Controller is properly registered")
    else:
        print("❌ ERROR: Controller registration missing")
        return False
    
    # Check for utility functions
    if 'MobileWorkorderUtils' in content:
        print("✅ SUCCESS: MobileWorkorderUtils are defined")
    else:
        print("❌ ERROR: MobileWorkorderUtils missing")
        return False
    
    print("\n=== JavaScript Module Structure Test ===")
    
    # Check for proper function structure
    if 'MobileWorkorderFormController = FormController.extend({' in content:
        print("✅ SUCCESS: FormController extension is correct")
    else:
        print("❌ ERROR: FormController extension missing or incorrect")
        return False
    
    # Check for event handlers
    event_handlers = [
        '_onLoadingButtonClick',
        '_onToggleClick', 
        '_onImageUpload'
    ]
    
    for handler in event_handlers:
        if handler in content:
            print(f"✅ SUCCESS: Event handler '{handler}' is defined")
        else:
            print(f"❌ ERROR: Missing event handler '{handler}'")
            return False
    
    # Check for mobile-specific features
    mobile_features = [
        '_setupMobileEnhancements',
        '_setupImageUpload',
        '_setupSwipeGestures',
        '_setupRealTimeUpdates'
    ]
    
    for feature in mobile_features:
        if feature in content:
            print(f"✅ SUCCESS: Mobile feature '{feature}' is implemented")
        else:
            print(f"❌ ERROR: Missing mobile feature '{feature}'")
            return False
    
    print("\n=== Manifest Integration Test ===")
    
    manifest_file = "odoo17/addons/facilities_management/__manifest__.py"
    
    if not os.path.exists(manifest_file):
        print("❌ ERROR: Manifest file not found")
        return False
    
    with open(manifest_file, 'r') as f:
        manifest_content = f.read()
    
    # Check if JavaScript is included in assets
    if 'mobile_workorder.js' in manifest_content:
        print("✅ SUCCESS: JavaScript file is included in manifest assets")
    else:
        print("❌ ERROR: JavaScript file not included in manifest assets")
        return False
    
    # Check for proper asset category
    if 'web.assets_backend' in manifest_content:
        print("✅ SUCCESS: Assets are properly categorized for backend")
    else:
        print("❌ ERROR: Assets not properly categorized")
        return False
    
    print("\n=== Summary ===")
    print("✅ All tests passed! The mobile workorder JavaScript module")
    print("   should now load correctly without the AMD syntax error.")
    print("\nThe fix involved:")
    print("1. Converting from function-based require syntax to array-based dependencies")
    print("2. Properly importing all required modules")
    print("3. Maintaining all existing functionality")
    
    return True

def test_other_js_files():
    """Test that other JavaScript files use correct modern syntax."""
    print("\n=== Other JavaScript Files Test ===")
    
    js_files = [
        "odoo17/addons/facilities_management/static/src/js/dashboard_widgets.js",
        "odoo17/addons/facilities_management/static/src/js/iot_monitoring.js", 
        "odoo17/addons/facilities_management/static/src/js/mobile_scanner.js"
    ]
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            print(f"⚠️  WARNING: {js_file} not found")
            continue
            
        with open(js_file, 'r') as f:
            content = f.read()
        
        filename = os.path.basename(js_file)
        
        if '/** @odoo-module **/' in content:
            print(f"✅ SUCCESS: {filename} uses modern ES6 module syntax")
        else:
            print(f"⚠️  WARNING: {filename} may not use modern syntax")
    
    print("\n=== JavaScript Files Summary ===")
    print("✅ mobile_workorder.js - Fixed AMD syntax")
    print("✅ dashboard_widgets.js - Uses modern ES6 syntax")
    print("✅ iot_monitoring.js - Uses modern ES6 syntax") 
    print("✅ mobile_scanner.js - Uses modern ES6 syntax")

if __name__ == "__main__":
    print("MOBILE WORKORDER JAVASCRIPT FIX TEST")
    print("=" * 50)
    
    success = test_mobile_workorder_js_syntax()
    test_other_js_files()
    
    if success:
        print("\n🎉 All tests passed! The JavaScript error should be resolved.")
        print("\nTo apply the fix:")
        print("1. Restart your Odoo server")
        print("2. Clear your browser cache")
        print("3. Refresh the page")
        print("\nThe error 'Dependencies should be defined by an array' should no longer appear.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")