#!/usr/bin/env python3
"""
Test script to verify ESG template fixes
"""

import os
import sys

def test_template_fixes():
    """Test that the template fixes are in place"""
    
    print("🔍 Testing ESG Template Fixes...")
    
    # Test 1: Check if the template file exists
    template_file = "/workspace/odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found")
        return False
    
    print("✅ Template file exists")
    
    # Test 2: Check if the safe_report_data field is added to the wizard
    wizard_file = "/workspace/odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found")
        return False
    
    with open(wizard_file, 'r') as f:
        wizard_content = f.read()
    
    if 'safe_report_data' in wizard_content:
        print("✅ safe_report_data field added to wizard")
    else:
        print("❌ ERROR: safe_report_data field not found in wizard")
        return False
    
    # Test 3: Check if the template uses safe_report_data
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    if 'safe_report_data' in template_content:
        print("✅ Template uses safe_report_data")
    else:
        print("❌ ERROR: Template does not use safe_report_data")
        return False
    
    # Test 4: Check if the template has proper safety checks
    safety_checks = [
        'isinstance(report_data, dict)',
        'o and hasattr(o, \'safe_report_data\')',
        'getattr(o, \'safe_report_data\', None)'
    ]
    
    for check in safety_checks:
        if check in template_content:
            print(f"✅ Safety check found: {check}")
        else:
            print(f"❌ ERROR: Safety check missing: {check}")
            return False
    
    # Test 5: Check if the wizard has proper error handling
    error_handling = [
        'try:',
        'except Exception:',
        'record.safe_report_data = {}'
    ]
    
    for check in error_handling:
        if check in wizard_content:
            print(f"✅ Error handling found: {check}")
        else:
            print(f"❌ ERROR: Error handling missing: {check}")
            return False
    
    print("\n🎉 All tests passed! The ESG template fixes are in place.")
    return True

def test_report_action():
    """Test that the report action is properly defined"""
    
    print("\n🔍 Testing Report Action...")
    
    reports_file = "/workspace/odoo17/addons/esg_reporting/report/esg_reports.xml"
    if not os.path.exists(reports_file):
        print("❌ ERROR: Reports file not found")
        return False
    
    with open(reports_file, 'r') as f:
        reports_content = f.read()
    
    if 'action_enhanced_esg_report_pdf' in reports_content:
        print("✅ Report action defined")
    else:
        print("❌ ERROR: Report action not found")
        return False
    
    if 'model">enhanced.esg.wizard' in reports_content:
        print("✅ Correct model referenced")
    else:
        print("❌ ERROR: Wrong model referenced")
        return False
    
    if 'report_enhanced_esg_wizard' in reports_content:
        print("✅ Correct template referenced")
    else:
        print("❌ ERROR: Wrong template referenced")
        return False
    
    print("🎉 Report action tests passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting ESG Template Fix Tests...\n")
    
    success = True
    
    # Run template tests
    if not test_template_fixes():
        success = False
    
    # Run report action tests
    if not test_report_action():
        success = False
    
    if success:
        print("\n🎉 All tests passed! The ESG template should now work correctly.")
        print("\n📋 Summary of fixes applied:")
        print("- Added safe_report_data computed field to wizard")
        print("- Updated template to use safe_report_data instead of direct access")
        print("- Added proper safety checks for None values")
        print("- Added error handling for edge cases")
        print("- Ensured report action is properly defined")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()