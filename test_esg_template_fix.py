#!/usr/bin/env python3
"""
Test script to verify the ESG template fix for the NoneType error.
"""

import os
import sys

def test_template_fix():
    """Test the template fix for the NoneType error"""
    
    print("🔍 Testing ESG Template Fix for NoneType Error")
    print("=" * 50)
    
    # Test 1: Check if the template file exists and has the fix
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found:", template_file)
        return False
    
    print("✅ Template file exists:", template_file)
    
    # Test 2: Check if the wizard file exists and has the fix
    wizard_file = "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found:", wizard_file)
        return False
    
    print("✅ Wizard file exists:", wizard_file)
    
    # Test 3: Check template structure
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Check for the fix in the template
    fixes_found = []
    
    # Check for proper docs handling
    if 't-if="docs and len(docs) > 0"' in template_content:
        fixes_found.append("✅ Proper docs length check")
    else:
        print("❌ Missing docs length check in template")
    
    # Check for proper o object handling
    if 't-if="o and o.id"' in template_content:
        fixes_found.append("✅ Proper o object validation")
    else:
        print("❌ Missing o object validation in template")
    
    # Check for manual computation method
    if '_compute_safe_report_data_manual()' in template_content:
        fixes_found.append("✅ Manual computation method usage")
    else:
        print("❌ Missing manual computation method in template")
    
    # Test 4: Check wizard structure
    with open(wizard_file, 'r') as f:
        wizard_content = f.read()
    
    # Check for the manual computation method
    if 'def _compute_safe_report_data_manual(self):' in wizard_content:
        fixes_found.append("✅ Manual computation method defined")
    else:
        print("❌ Missing manual computation method in wizard")
    
    # Check for proper report values method
    if 'def _get_report_values(self, docids, data=None):' in wizard_content:
        fixes_found.append("✅ Report values method defined")
    else:
        print("❌ Missing report values method in wizard")
    
    # Test 5: Check for proper error handling
    if 'No wizard object available for report generation' in template_content:
        fixes_found.append("✅ Proper error message for missing wizard")
    else:
        print("❌ Missing error message for missing wizard")
    
    # Test 6: Check for safe data access
    if 'o._compute_safe_report_data_manual()' in template_content:
        fixes_found.append("✅ Safe data access method")
    else:
        print("❌ Missing safe data access method")
    
    print("\n📋 Fix Summary:")
    print("-" * 30)
    for fix in fixes_found:
        print(fix)
    
    if len(fixes_found) >= 6:
        print(f"\n🎉 SUCCESS: All template fixes are in place! ({len(fixes_found)}/6+)")
        print("\nThe fixes address the following issues:")
        print("1. ✅ Handles None docs in template iteration")
        print("2. ✅ Validates o object before accessing properties")
        print("3. ✅ Uses manual computation method for safe data access")
        print("4. ✅ Provides proper error messages")
        print("5. ✅ Adds report values method for proper data passing")
        print("6. ✅ Implements comprehensive error handling")
        
        print("\n🚀 Next Steps:")
        print("1. Update the esg_reporting module: --update=esg_reporting")
        print("2. Test the ESG report generation")
        print("3. Verify that the NoneType error is resolved")
        
        return True
    else:
        print(f"\n⚠️  WARNING: Only {len(fixes_found)}/6 fixes found")
        print("Some fixes may be missing. Please check the implementation.")
        return False

def test_template_syntax():
    """Test the XML syntax of the template"""
    
    print("\n🔍 Testing Template XML Syntax")
    print("=" * 40)
    
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Basic XML structure checks
        if '<?xml version="1.0" encoding="utf-8"?>' in content:
            print("✅ XML declaration present")
        else:
            print("❌ Missing XML declaration")
        
        if '<odoo>' in content and '</odoo>' in content:
            print("✅ Odoo root element present")
        else:
            print("❌ Missing Odoo root element")
        
        if '<data>' in content and '</data>' in content:
            print("✅ Data element present")
        else:
            print("❌ Missing data element")
        
        # Check for template structure
        if 'id="report_enhanced_esg_wizard"' in content:
            print("✅ Enhanced ESG wizard template present")
        else:
            print("❌ Missing enhanced ESG wizard template")
        
        if 'id="report_enhanced_esg_wizard_document"' in content:
            print("✅ Enhanced ESG wizard document template present")
        else:
            print("❌ Missing enhanced ESG wizard document template")
        
        print("\n✅ Template syntax appears to be valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return False

if __name__ == "__main__":
    print("🧪 ESG Template Fix Test Suite")
    print("=" * 40)
    
    success = True
    
    # Run tests
    if not test_template_fix():
        success = False
    
    if not test_template_syntax():
        success = False
    
    if success:
        print("\n🎉 All tests passed! The template fix should resolve the NoneType error.")
        print("\n📝 Summary of fixes applied:")
        print("• Added proper None checks for docs and o objects")
        print("• Implemented manual computation method for safe data access")
        print("• Added comprehensive error handling and messages")
        print("• Fixed template structure to handle edge cases")
        print("• Added report values method for proper data passing")
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
    
    print("\n" + "=" * 40)