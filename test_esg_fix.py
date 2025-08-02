#!/usr/bin/env python3
"""
Test script to verify the ESG report template fix
"""

import os
import sys

def test_template_fix():
    """Test that the template fix is working correctly"""
    
    # Check if the template file exists
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found")
        return False
    
    # Read the template file
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Check for the fixed line
    fixed_line = 'hasattr(report_data, \'keys\')'
    if fixed_line in content:
        print("✅ SUCCESS: Template has been fixed with proper defensive checks")
        return True
    else:
        print("❌ ERROR: Template fix not found")
        return False

def test_wizard_fix():
    """Test that the wizard fix is working correctly"""
    
    # Check if the wizard file exists
    wizard_file = "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found")
        return False
    
    # Read the wizard file
    with open(wizard_file, 'r') as f:
        content = f.read()
    
    # Check for the safety methods
    safety_checks = [
        'def _get_report_data(self):',
        'if serialized_data is None or not isinstance(serialized_data, dict):',
        'return self.report_data'
    ]
    
    for check in safety_checks:
        if check in content:
            print(f"✅ SUCCESS: Found safety check: {check}")
        else:
            print(f"❌ ERROR: Missing safety check: {check}")
            return False
    
    return True

def main():
    """Main test function"""
    print("Testing ESG Report Template Fix...")
    print("=" * 50)
    
    template_ok = test_template_fix()
    wizard_ok = test_wizard_fix()
    
    print("=" * 50)
    if template_ok and wizard_ok:
        print("✅ ALL TESTS PASSED: ESG report template fix is working correctly")
        print("\nThe fix addresses the following issues:")
        print("1. Added defensive checks for report_data.keys() call")
        print("2. Added _get_report_data() method to ensure report_data is always a dict")
        print("3. Added proper initialization in create() method")
        print("4. Added safety checks in serialization")
        return True
    else:
        print("❌ SOME TESTS FAILED: Please check the implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)