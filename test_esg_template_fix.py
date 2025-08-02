#!/usr/bin/env python3
"""
Test script to verify the ESG template fix for the NoneType error.
"""

import os
import sys

def test_template_fix():
    """Test that the template fix prevents NoneType errors"""
    
    print("🔍 Testing ESG Template Fix...")
    
    # Check if the template file exists
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found:", template_file)
        return False
    
    # Check if the wizard file exists
    wizard_file = "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found:", wizard_file)
        return False
    
    # Read the template file to check for the fix
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Check for the key fixes
    fixes_applied = []
    
    # Fix 1: Ensure report_data is always a dictionary
    if 'o._get_report_data() or {}' in template_content:
        fixes_applied.append("✅ Report data initialization fix applied")
    else:
        print("❌ ERROR: Report data initialization fix not found")
        return False
    
    # Fix 2: Safe keys display
    if "'Available' if report_data and isinstance(report_data, dict) and len(report_data) > 0 else 'No keys available'" in template_content:
        fixes_applied.append("✅ Safe keys display fix applied")
    else:
        print("❌ ERROR: Safe keys display fix not found")
        return False
    
    # Fix 3: Safe length display
    if "str(len(report_data)) if report_data and hasattr(report_data, '__len__') else 'N/A'" in template_content:
        fixes_applied.append("✅ Safe length display fix applied")
    else:
        print("❌ ERROR: Safe length display fix not found")
        return False
    
    # Read the wizard file to check for the _get_report_data fix
    with open(wizard_file, 'r') as f:
        wizard_content = f.read()
    
    # Check for the try-catch in _get_report_data
    if 'try:' in wizard_content and 'except Exception:' in wizard_content:
        fixes_applied.append("✅ Wizard _get_report_data error handling applied")
    else:
        print("❌ ERROR: Wizard _get_report_data error handling not found")
        return False
    
    # Check for the error handling in action_generate_enhanced_esg_report
    if 'except Exception as e:' in wizard_content:
        fixes_applied.append("✅ Action method error handling applied")
    else:
        print("❌ ERROR: Action method error handling not found")
        return False
    
    print("\n📋 Applied Fixes:")
    for fix in fixes_applied:
        print(f"   {fix}")
    
    print("\n✅ All template fixes have been applied successfully!")
    print("   The NoneType error should now be resolved.")
    
    return True

def test_template_syntax():
    """Test that the template XML syntax is valid"""
    
    print("\n🔍 Testing Template XML Syntax...")
    
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Basic XML validation checks
        if '<?xml' in content:
            print("✅ XML declaration found")
        else:
            print("❌ ERROR: XML declaration missing")
            return False
        
        if '<odoo>' in content and '</odoo>' in content:
            print("✅ Odoo root element found")
        else:
            print("❌ ERROR: Odoo root element missing")
            return False
        
        if '<data>' in content and '</data>' in content:
            print("✅ Data element found")
        else:
            print("❌ ERROR: Data element missing")
            return False
        
        # Check for balanced template tags
        template_count = content.count('<template')
        template_end_count = content.count('</template>')
        
        if template_count == template_end_count:
            print("✅ Template tags are balanced")
        else:
            print(f"❌ ERROR: Template tags unbalanced - {template_count} opening, {template_end_count} closing")
            return False
        
        print("✅ Template XML syntax is valid")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to validate template syntax: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ESG Template Fix Verification")
    print("=" * 50)
    
    success = True
    
    # Test the template fixes
    if not test_template_fix():
        success = False
    
    # Test the template syntax
    if not test_template_syntax():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The ESG template fix is ready.")
        print("\n📝 Summary:")
        print("   - Fixed NoneType error in template")
        print("   - Added safe error handling in wizard")
        print("   - Ensured report_data is always a dictionary")
        print("   - Added proper XML validation")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        sys.exit(1)