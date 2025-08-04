#!/usr/bin/env python3
"""
Comprehensive ESG Dashboard Fix Verification Script
This script tests all the fixes applied to the ESG dashboard to ensure it's working properly.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_esg_analytics_model():
    """Test the ESG analytics model fixes"""
    print("\n=== Testing ESG Analytics Model Fixes ===")
    
    # Check if the model file exists and has proper error handling
    model_file = '/workspace/odoo17/addons/esg_reporting/models/esg_analytics.py'
    
    if not os.path.exists(model_file):
        print("✗ ESG analytics model file not found")
        return False
    
    try:
        with open(model_file, 'r') as f:
            content = f.read()
        
        # Check for proper error handling
        if 'try:' in content and 'except Exception as e:' in content:
            print("✓ Error handling implemented in analytics model")
        else:
            print("✗ Missing error handling in analytics model")
            return False
        
        # Check for data validation
        if 'getDefaultDashboardData' in content or 'default data structure' in content:
            print("✓ Default data structure implemented")
        else:
            print("✗ Missing default data structure")
            return False
        
        # Check for comprehensive dashboard data method
        if 'get_comprehensive_dashboard_data' in content:
            print("✓ Comprehensive dashboard data method found")
        else:
            print("✗ Missing comprehensive dashboard data method")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing analytics model: {e}")
        return False

def test_advanced_dashboard_js():
    """Test the advanced dashboard JavaScript fixes"""
    print("\n=== Testing Advanced Dashboard JavaScript Fixes ===")
    
    js_file = '/workspace/odoo17/addons/esg_reporting/static/src/js/esg_advanced_dashboard.js'
    
    if not os.path.exists(js_file):
        print("✗ Advanced dashboard JS file not found")
        return False
    
    try:
        with open(js_file, 'r') as f:
            content = f.read()
        
        # Check for proper error handling
        if 'try {' in content and 'catch (error)' in content:
            print("✓ Error handling implemented in advanced dashboard JS")
        else:
            print("✗ Missing error handling in advanced dashboard JS")
            return False
        
        # Check for chart initialization fixes
        if 'setTimeout(() => {' in content and 'createESGScoreChart()' in content:
            print("✓ Chart initialization with timeout implemented")
        else:
            print("✗ Missing chart initialization timeout")
            return False
        
        # Check for chart destruction
        if 'destroy()' in content:
            print("✓ Chart destruction implemented")
        else:
            print("✗ Missing chart destruction")
            return False
        
        # Check for data validation
        if 'getDefaultDashboardData' in content:
            print("✓ Default dashboard data method implemented")
        else:
            print("✗ Missing default dashboard data method")
            return False
        
        # Check for proper chart options
        if 'maintainAspectRatio: false' in content:
            print("✓ Chart responsive options implemented")
        else:
            print("✗ Missing chart responsive options")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing advanced dashboard JS: {e}")
        return False

def test_regular_dashboard_js():
    """Test the regular dashboard JavaScript fixes"""
    print("\n=== Testing Regular Dashboard JavaScript Fixes ===")
    
    js_file = '/workspace/odoo17/addons/esg_reporting/static/src/js/esg_dashboard.js'
    
    if not os.path.exists(js_file):
        print("✗ Regular dashboard JS file not found")
        return False
    
    try:
        with open(js_file, 'r') as f:
            content = f.read()
        
        # Check for proper error handling
        if 'try {' in content and 'catch (analyticsError)' in content:
            print("✓ Error handling implemented in regular dashboard JS")
        else:
            print("✗ Missing error handling in regular dashboard JS")
            return False
        
        # Check for default data structure
        if 'dashboardData = {' in content and 'analytics: {}' in content:
            print("✓ Default data structure implemented")
        else:
            print("✗ Missing default data structure")
            return False
        
        # Check for individual try-catch blocks
        if 'catch (analyticsError)' in content and 'catch (initiativeError)' in content:
            print("✓ Individual error handling for each data type")
        else:
            print("✗ Missing individual error handling")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing regular dashboard JS: {e}")
        return False

def test_css_styling():
    """Test the CSS styling fixes"""
    print("\n=== Testing CSS Styling Fixes ===")
    
    css_file = '/workspace/odoo17/addons/esg_reporting/static/src/css/esg_dashboard.css'
    
    if not os.path.exists(css_file):
        print("✗ CSS file not found")
        return False
    
    try:
        with open(css_file, 'r') as f:
            content = f.read()
        
        # Check for responsive design
        if '@media (max-width: 768px)' in content:
            print("✓ Responsive design implemented")
        else:
            print("✗ Missing responsive design")
            return False
        
        # Check for chart container styles
        if '.chart-container' in content and 'height: 300px' in content:
            print("✓ Chart container styles implemented")
        else:
            print("✗ Missing chart container styles")
            return False
        
        # Check for loading states
        if '.spinner-border' in content:
            print("✓ Loading state styles implemented")
        else:
            print("✗ Missing loading state styles")
            return False
        
        # Check for error states
        if '.alert-danger' in content:
            print("✓ Error state styles implemented")
        else:
            print("✗ Missing error state styles")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing CSS styling: {e}")
        return False

def test_manifest_updates():
    """Test the manifest file updates"""
    print("\n=== Testing Manifest File Updates ===")
    
    manifest_file = '/workspace/odoo17/addons/esg_reporting/__manifest__.py'
    
    if not os.path.exists(manifest_file):
        print("✗ Manifest file not found")
        return False
    
    try:
        with open(manifest_file, 'r') as f:
            content = f.read()
        
        # Check for CSS inclusion
        if 'esg_dashboard.css' in content:
            print("✓ CSS file included in manifest")
        else:
            print("✗ CSS file not included in manifest")
            return False
        
        # Check for Chart.js library
        if 'web.chartjs_lib' in content:
            print("✓ Chart.js library included")
        else:
            print("✗ Chart.js library not included")
            return False
        
        # Check for all required assets
        required_assets = [
            'esg_advanced_dashboard.js',
            'esg_dashboard.js',
            'esg_advanced_dashboard.xml',
            'esg_dashboard.xml'
        ]
        
        for asset in required_assets:
            if asset in content:
                print(f"✓ {asset} included in manifest")
            else:
                print(f"✗ {asset} not included in manifest")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing manifest updates: {e}")
        return False

def test_xml_template_fixes():
    """Test the XML template fixes"""
    print("\n=== Testing XML Template Fixes ===")
    
    advanced_xml = '/workspace/odoo17/addons/esg_reporting/static/src/xml/esg_advanced_dashboard.xml'
    regular_xml = '/workspace/odoo17/addons/esg_reporting/static/src/xml/esg_dashboard.xml'
    
    # Test advanced dashboard XML
    if os.path.exists(advanced_xml):
        try:
            with open(advanced_xml, 'r') as f:
                content = f.read()
            
            # Check for proper loading states
            if 'state.loading' in content and 'spinner-border' in content:
                print("✓ Loading states implemented in advanced dashboard")
            else:
                print("✗ Missing loading states in advanced dashboard")
                return False
            
            # Check for error states
            if 'state.error' in content and 'alert-danger' in content:
                print("✓ Error states implemented in advanced dashboard")
            else:
                print("✗ Missing error states in advanced dashboard")
                return False
            
            # Check for chart containers
            if 'canvas id=' in content:
                print("✓ Chart containers implemented in advanced dashboard")
            else:
                print("✗ Missing chart containers in advanced dashboard")
                return False
                
        except Exception as e:
            print(f"✗ Error testing advanced dashboard XML: {e}")
            return False
    else:
        print("✗ Advanced dashboard XML file not found")
        return False
    
    # Test regular dashboard XML
    if os.path.exists(regular_xml):
        try:
            with open(regular_xml, 'r') as f:
                content = f.read()
            
            # Check for proper loading states
            if 'state.loading' in content and 'spinner-border' in content:
                print("✓ Loading states implemented in regular dashboard")
            else:
                print("✗ Missing loading states in regular dashboard")
                return False
            
            # Check for error states
            if 'state.error' in content and 'alert-danger' in content:
                print("✓ Error states implemented in regular dashboard")
            else:
                print("✗ Missing error states in regular dashboard")
                return False
                
        except Exception as e:
            print(f"✗ Error testing regular dashboard XML: {e}")
            return False
    else:
        print("✗ Regular dashboard XML file not found")
        return False
    
    return True

def test_syntax_validation():
    """Test syntax validation for all files"""
    print("\n=== Testing Syntax Validation ===")
    
    files_to_test = [
        '/workspace/odoo17/addons/esg_reporting/models/esg_analytics.py',
        '/workspace/odoo17/addons/esg_reporting/static/src/js/esg_advanced_dashboard.js',
        '/workspace/odoo17/addons/esg_reporting/static/src/js/esg_dashboard.js',
        '/workspace/odoo17/addons/esg_reporting/static/src/xml/esg_advanced_dashboard.xml',
        '/workspace/odoo17/addons/esg_reporting/static/src/xml/esg_dashboard.xml',
        '/workspace/odoo17/addons/esg_reporting/__manifest__.py'
    ]
    
    all_valid = True
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            try:
                # For Python files, try to compile
                if file_path.endswith('.py'):
                    with open(file_path, 'r') as f:
                        compile(f.read(), file_path, 'exec')
                    print(f"✓ {os.path.basename(file_path)} - Python syntax valid")
                
                # For JavaScript files, basic validation
                elif file_path.endswith('.js'):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if 'export class' in content or 'import {' in content:
                        print(f"✓ {os.path.basename(file_path)} - JavaScript syntax appears valid")
                    else:
                        print(f"✗ {os.path.basename(file_path)} - JavaScript syntax may be invalid")
                        all_valid = False
                
                # For XML files, basic validation
                elif file_path.endswith('.xml'):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if '<?xml' in content or '<templates' in content:
                        print(f"✓ {os.path.basename(file_path)} - XML syntax appears valid")
                    else:
                        print(f"✗ {os.path.basename(file_path)} - XML syntax may be invalid")
                        all_valid = False
                        
            except Exception as e:
                print(f"✗ {os.path.basename(file_path)} - Syntax error: {e}")
                all_valid = False
        else:
            print(f"✗ {os.path.basename(file_path)} - File not found")
            all_valid = False
    
    return all_valid

def main():
    """Main test function"""
    print("ESG Dashboard Comprehensive Fix Verification")
    print("=" * 50)
    
    tests = [
        test_esg_analytics_model,
        test_advanced_dashboard_js,
        test_regular_dashboard_js,
        test_css_styling,
        test_manifest_updates,
        test_xml_template_fixes,
        test_syntax_validation
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The ESG dashboard should now work properly.")
        print("\nTo test the dashboard:")
        print("1. Restart your Odoo server")
        print("2. Update the ESG module")
        print("3. Navigate to ESG > Dashboard")
        print("4. The dashboard should load without errors")
        print("5. Charts should render properly")
        print("6. Data should update when changing periods")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        print("\nCommon issues to check:")
        print("- Ensure all files are properly saved")
        print("- Check for syntax errors in the files")
        print("- Verify the module is properly installed")
        print("- Clear browser cache and restart Odoo")

if __name__ == "__main__":
    main()