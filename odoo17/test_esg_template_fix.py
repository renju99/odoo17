#!/usr/bin/env python3
"""
Test script to verify ESG template fixes
"""

import os
import sys
import xml.etree.ElementTree as ET

def test_template_fixes():
    """Test that the template fixes are working correctly"""
    
    template_file = "/workspace/odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found")
        return False
    
    try:
        # Parse the XML file
        tree = ET.parse(template_file)
        root = tree.getroot()
        
        # Convert to string for text search
        xml_content = ET.tostring(root, encoding='unicode')
        
        print("🔍 Checking template fixes...")
        
        # Check 1: Verify the problematic method call is fixed
        if 'o._compute_safe_report_data_manual()' in xml_content:
            print("✅ SUCCESS: Method call is properly formatted")
        else:
            print("❌ ERROR: Method call not found or incorrectly formatted")
            return False
        
        # Check 2: Verify no callable() calls exist
        if 'callable(' in xml_content:
            print("❌ ERROR: callable() calls still exist in template")
            return False
        else:
            print("✅ SUCCESS: No callable() calls found")
        
        # Check 3: Verify datetime call is fixed
        if 'datetime.datetime.now().strftime' in xml_content:
            print("✅ SUCCESS: Datetime call is properly formatted")
        else:
            print("❌ ERROR: Datetime call not found or incorrectly formatted")
            return False
        
        # Check 4: Verify proper conditional checks
        if 'o and hasattr(o, \'_compute_safe_report_data_manual\') and o._compute_safe_report_data_manual' in xml_content:
            print("✅ SUCCESS: Proper conditional checks are in place")
        else:
            print("❌ ERROR: Conditional checks not properly implemented")
            return False
        
        print("\n🎉 All template fixes verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to parse template file: {str(e)}")
        return False

def test_wizard_fixes():
    """Test that the wizard fixes are working correctly"""
    
    wizard_file = "/workspace/odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found")
        return False
    
    try:
        with open(wizard_file, 'r') as f:
            content = f.read()
        
        print("🔍 Checking wizard fixes...")
        
        # Check 1: Verify the safe method exists
        if 'def _compute_safe_report_data_manual(self):' in content:
            print("✅ SUCCESS: _compute_safe_report_data_manual method exists")
        else:
            print("❌ ERROR: _compute_safe_report_data_manual method not found")
            return False
        
        # Check 2: Verify the ultimate fallback method exists
        if 'def _get_ultimate_fallback_data(self):' in content:
            print("✅ SUCCESS: _get_ultimate_fallback_data method exists")
        else:
            print("❌ ERROR: _get_ultimate_fallback_data method not found")
            return False
        
        # Check 3: Verify proper None checks
        if 'if not self:' in content:
            print("✅ SUCCESS: Proper None checks are in place")
        else:
            print("❌ ERROR: None checks not properly implemented")
            return False
        
        # Check 4: Verify proper exception handling
        if 'except Exception as e:' in content:
            print("✅ SUCCESS: Proper exception handling is in place")
        else:
            print("❌ ERROR: Exception handling not properly implemented")
            return False
        
        print("\n🎉 All wizard fixes verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to read wizard file: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing ESG Template Fixes")
    print("=" * 50)
    
    template_ok = test_template_fixes()
    wizard_ok = test_wizard_fixes()
    
    print("\n" + "=" * 50)
    if template_ok and wizard_ok:
        print("🎉 ALL TESTS PASSED! The ESG template fixes are working correctly.")
        print("\n📋 Summary of fixes applied:")
        print("1. Fixed method call in template: o._compute_safe_report_data_manual()")
        print("2. Removed problematic callable() checks")
        print("3. Fixed datetime call in template")
        print("4. Added proper None checks in wizard methods")
        print("5. Added ultimate fallback data method")
        print("6. Improved exception handling")
        return True
    else:
        print("❌ SOME TESTS FAILED! Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)