#!/usr/bin/env python3

import sys
import os

# Add the Odoo path
sys.path.insert(0, '/workspace/odoo17')

def test_sla_fields():
    """Test to verify SLA field names"""
    
    # Test the workorder_sla_integration.py file
    integration_file = "/workspace/odoo17/addons/facilities_management/models/workorder_sla_integration.py"
    
    print("Testing workorder_sla_integration.py file...")
    
    with open(integration_file, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'critical_threshold' in line and 'sla_id' in line:
            print(f"Line {i}: {line.strip()}")
            if 'critical_threshold_hours' in line:
                print("✓ Using correct field name: critical_threshold_hours")
            elif 'critical_threshold' in line and 'critical_threshold_hours' not in line:
                print("✗ Using incorrect field name: critical_threshold")
    
    print("\nTesting facilities.sla model fields...")
    
    # Test the facilities.sla model
    sla_file = "/workspace/odoo17/addons/facilities_management/models/sla.py"
    
    with open(sla_file, 'r') as f:
        lines = f.readlines()
    
    critical_threshold_hours_found = False
    warning_threshold_hours_found = False
    
    for i, line in enumerate(lines, 1):
        if 'critical_threshold_hours' in line:
            critical_threshold_hours_found = True
            print(f"Line {i}: Found critical_threshold_hours")
        if 'warning_threshold_hours' in line:
            warning_threshold_hours_found = True
            print(f"Line {i}: Found warning_threshold_hours")
    
    if critical_threshold_hours_found:
        print("✓ critical_threshold_hours field exists in facilities.sla")
    else:
        print("✗ critical_threshold_hours field missing in facilities.sla")
    
    if warning_threshold_hours_found:
        print("✓ warning_threshold_hours field exists in facilities.sla")
    else:
        print("✗ warning_threshold_hours field missing in facilities.sla")

if __name__ == "__main__":
    test_sla_fields()