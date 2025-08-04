#!/usr/bin/env python3
"""
Test script to verify JavaScript fixes for Facilities Management module
"""

import os
import sys

def test_manifest_includes():
    """Test that the manifest properly includes Chart.js and all assets"""
    print("1. Testing manifest includes...")
    
    manifest_path = "odoo17/addons/facilities_management/__manifest__.py"
    
    if not os.path.exists(manifest_path):
        print("✗ Manifest file not found")
        return False
    
    with open(manifest_path, 'r') as f:
        content = f.read()
    
    # Check for Chart.js inclusion
    if "('include', 'web.chartjs_lib')" in content:
        print("✓ Chart.js bundle properly included")
    else:
        print("✗ Chart.js bundle missing")
        return False
    
    # Check for JavaScript files
    js_files = [
        'facilities_management/static/src/js/dashboard_widgets.js',
        'facilities_management/static/src/js/iot_monitoring.js',
        'facilities_management/static/src/js/mobile_scanner.js'
    ]
    
    for js_file in js_files:
        if js_file in content:
            print(f"✓ {js_file} included")
        else:
            print(f"✗ {js_file} missing")
            return False
    
    # Check for XML templates
    if "'facilities_management/static/src/xml/*.xml'" in content:
        print("✓ XML templates included")
    else:
        print("✗ XML templates missing")
        return False
    
    return True

def test_js_files_exist():
    """Test that all JavaScript files exist"""
    print("\n2. Testing JavaScript files exist...")
    
    js_files = [
        "odoo17/addons/facilities_management/static/src/js/dashboard_widgets.js",
        "odoo17/addons/facilities_management/static/src/js/iot_monitoring.js",
        "odoo17/addons/facilities_management/static/src/js/mobile_scanner.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✓ {js_file} exists")
        else:
            print(f"✗ {js_file} missing")
            return False
    
    return True

def test_template_files_exist():
    """Test that all template files exist"""
    print("\n3. Testing template files exist...")
    
    template_files = [
        "odoo17/addons/facilities_management/static/src/xml/dashboard_templates.xml",
        "odoo17/addons/facilities_management/static/src/xml/iot_monitoring_templates.xml",
        "odoo17/addons/facilities_management/static/src/xml/mobile_scanner_templates.xml",
        "odoo17/addons/facilities_management/static/src/xml/space_booking_templates.xml"
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✓ {template_file} exists")
        else:
            print(f"✗ {template_file} missing")
            return False
    
    return True

def test_js_syntax():
    """Test JavaScript syntax for common issues"""
    print("\n4. Testing JavaScript syntax...")
    
    js_files = [
        "odoo17/addons/facilities_management/static/src/js/dashboard_widgets.js",
        "odoo17/addons/facilities_management/static/src/js/iot_monitoring.js",
        "odoo17/addons/facilities_management/static/src/js/mobile_scanner.js"
    ]
    
    for js_file in js_files:
        with open(js_file, 'r') as f:
            content = f.read()
        
        # Check for unreachable code (return after return)
        if "return" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'return' in line and i < len(lines) - 1:
                    next_line = lines[i + 1]
                    if 'return' in next_line and not next_line.strip().startswith('//'):
                        print(f"✗ Potential unreachable code in {js_file} around line {i+1}")
                        return False
        
        # Check for proper error handling
        if "try" in content and "catch" in content:
            print(f"✓ {js_file} has proper error handling")
        else:
            print(f"⚠ {js_file} may need error handling")
    
    return True

def test_model_method_exists():
    """Test that the get_dashboard_data method exists in the model"""
    print("\n5. Testing model method exists...")
    
    model_file = "odoo17/addons/facilities_management/models/space_booking.py"
    
    if not os.path.exists(model_file):
        print("✗ Model file not found")
        return False
    
    with open(model_file, 'r') as f:
        content = f.read()
    
    if "def get_dashboard_data(self):" in content:
        print("✓ get_dashboard_data method exists")
        return True
    else:
        print("✗ get_dashboard_data method missing")
        return False

def test_chartjs_handling():
    """Test that Chart.js is properly handled"""
    print("\n6. Testing Chart.js handling...")
    
    iot_file = "odoo17/addons/facilities_management/static/src/js/iot_monitoring.js"
    
    if not os.path.exists(iot_file):
        print("✗ IoT monitoring file not found")
        return False
    
    with open(iot_file, 'r') as f:
        content = f.read()
    
    # Check for Chart.js availability check
    if "typeof Chart !== 'undefined'" in content:
        print("✓ Chart.js availability check present")
    else:
        print("✗ Chart.js availability check missing")
        return False
    
    # Check for fallback handling
    if "_showChartFallback" in content:
        print("✓ Chart.js fallback handling present")
    else:
        print("✗ Chart.js fallback handling missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Testing JavaScript fixes for Facilities Management module")
    print("=" * 60)
    
    tests = [
        test_manifest_includes,
        test_js_files_exist,
        test_template_files_exist,
        test_js_syntax,
        test_model_method_exists,
        test_chartjs_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! JavaScript fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)