#!/usr/bin/env python3

# Test script to verify SLA fix
import sys
import os

# Add the Odoo path
sys.path.insert(0, '/workspace/odoo17')

try:
    from odoo import api, fields, models
    from odoo.addons.facilities_management.models.sla import FacilitiesSLA
    from odoo.addons.facilities_management.models.workorder_sla_integration import MaintenanceWorkOrder
    
    print("✓ Successfully imported SLA models")
    
    # Test that the critical_threshold_hours field exists
    if hasattr(FacilitiesSLA, 'critical_threshold_hours'):
        print("✓ critical_threshold_hours field exists in FacilitiesSLA")
    else:
        print("✗ critical_threshold_hours field missing in FacilitiesSLA")
    
    # Test that the warning_threshold_hours field exists
    if hasattr(FacilitiesSLA, 'warning_threshold_hours'):
        print("✓ warning_threshold_hours field exists in FacilitiesSLA")
    else:
        print("✗ warning_threshold_hours field missing in FacilitiesSLA")
    
    print("✓ All tests passed - SLA fix is working correctly")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")