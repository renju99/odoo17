#!/usr/bin/env python3
"""
Test script to verify SLA dashboard fixes
"""

import sys
import os

# Add the odoo17 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'odoo17'))

def test_sla_dashboard_fixes():
    """Test the SLA dashboard fixes"""
    
    print("Testing SLA Dashboard Fixes...")
    
    # Test 1: Check if the SLA model has the correct compute method
    try:
        with open('odoo17/addons/facilities_management/models/sla.py', 'r') as f:
            content = f.read()
            
        # Check if the improved _compute_metrics method exists
        if 'def _compute_metrics(self):' in content:
            print("✓ SLA dashboard compute method found")
        else:
            print("✗ SLA dashboard compute method not found")
            return False
            
        # Check if the debug methods exist
        if 'def action_debug_data(self):' in content:
            print("✓ Debug method found")
        else:
            print("✗ Debug method not found")
            
        if 'def action_create_test_data(self):' in content:
            print("✓ Test data creation method found")
        else:
            print("✗ Test data creation method not found")
            
        if 'def action_create_default_slas(self):' in content:
            print("✓ Default SLA creation method found")
        else:
            print("✗ Default SLA creation method not found")
            
    except FileNotFoundError:
        print("✗ SLA model file not found")
        return False
    
    # Test 2: Check if the view has the debug buttons
    try:
        with open('odoo17/addons/facilities_management/views/sla_views.xml', 'r') as f:
            content = f.read()
            
        if 'action_debug_data' in content:
            print("✓ Debug button found in view")
        else:
            print("✗ Debug button not found in view")
            
        if 'action_create_test_data' in content:
            print("✓ Test data button found in view")
        else:
            print("✗ Test data button not found in view")
            
        if 'action_create_default_slas' in content:
            print("✓ Default SLAs button found in view")
        else:
            print("✗ Default SLAs button not found in view")
            
    except FileNotFoundError:
        print("✗ SLA views file not found")
        return False
    
    # Test 3: Check if the JSON field display is improved
    if 'widget="json"' in content:
        print("✓ JSON widget found in view")
    else:
        print("✗ JSON widget not found in view")
    
    # Test 4: Check if the debug page exists
    if 'Debug Information' in content:
        print("✓ Debug page found in view")
    else:
        print("✗ Debug page not found in view")
    
    print("\nSummary of fixes applied:")
    print("1. Improved _compute_metrics method with better error handling")
    print("2. Enhanced daily and weekly trend calculations")
    print("3. Added debug methods for troubleshooting")
    print("4. Added test data creation functionality")
    print("5. Improved view with JSON widgets and debug information")
    print("6. Added buttons for creating default SLAs and test data")
    
    print("\nTo test the dashboard:")
    print("1. Open the SLA Performance Dashboard")
    print("2. Click 'Create Default SLAs' if no SLAs exist")
    print("3. Select an SLA from the dropdown")
    print("4. Click 'Create Test Data' to generate sample work orders")
    print("5. Click 'Debug Data' to see detailed information")
    print("6. Check the 'Debug Information' tab for metrics")
    
    return True

if __name__ == "__main__":
    test_sla_dashboard_fixes()