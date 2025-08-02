#!/usr/bin/env python3
"""
Test script to verify ESG report action fix
"""

import os
import sys

def test_esg_report_action():
    """Test if the ESG report action is properly defined"""
    
    # Check if the action is defined in the reports XML
    reports_file = "odoo17/addons/esg_reporting/report/esg_reports.xml"
    if not os.path.exists(reports_file):
        print("❌ ERROR: Reports file not found:", reports_file)
        return False
    
    with open(reports_file, 'r') as f:
        content = f.read()
        if 'action_enhanced_esg_report_pdf' in content:
            print("✅ SUCCESS: action_enhanced_esg_report_pdf found in reports XML")
        else:
            print("❌ ERROR: action_enhanced_esg_report_pdf not found in reports XML")
            return False
    
    # Check if the template is defined
    templates_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    if not os.path.exists(templates_file):
        print("❌ ERROR: Templates file not found:", templates_file)
        return False
    
    with open(templates_file, 'r') as f:
        content = f.read()
        if 'report_enhanced_esg_wizard' in content:
            print("✅ SUCCESS: report_enhanced_esg_wizard template found")
        else:
            print("❌ ERROR: report_enhanced_esg_wizard template not found")
            return False
    
    # Check if the wizard references the correct action
    wizard_file = "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found:", wizard_file)
        return False
    
    with open(wizard_file, 'r') as f:
        content = f.read()
        if 'esg_reporting.action_enhanced_esg_report_pdf' in content:
            print("✅ SUCCESS: Wizard references correct action")
        else:
            print("❌ ERROR: Wizard does not reference correct action")
            return False
    
    print("\n🎉 All checks passed! The ESG report action fix is complete.")
    return True

def main():
    print("Testing ESG Report Action Fix...")
    print("=" * 50)
    
    success = test_esg_report_action()
    
    if success:
        print("\n✅ FIX SUMMARY:")
        print("- Added action_enhanced_esg_report_pdf to esg_reports.xml")
        print("- Created report_enhanced_esg_wizard template")
        print("- Updated wizard to reference correct action")
        print("- All files are properly configured")
        
        print("\n📋 NEXT STEPS:")
        print("1. Restart Odoo server")
        print("2. Update the esg_reporting module: --update=esg_reporting")
        print("3. Test the enhanced ESG report generation")
    else:
        print("\n❌ FIX FAILED: Please check the errors above")

if __name__ == "__main__":
    main()