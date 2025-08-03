#!/usr/bin/env python3
"""
Test script to validate the SLA performance report fix
"""

import xml.etree.ElementTree as ET
import os

def test_xml_syntax():
    """Test that the SLA performance report XML file is syntactically correct"""
    
    # Path to the SLA performance report file
    sla_report_path = "odoo17/addons/facilities_management/reports/sla_performance_report.xml"
    
    if not os.path.exists(sla_report_path):
        print(f"❌ Error: File {sla_report_path} does not exist")
        return False
    
    try:
        # Parse the XML file
        tree = ET.parse(sla_report_path)
        root = tree.getroot()
        
        # Check if it's a valid Odoo XML file
        if root.tag != 'odoo':
            print(f"❌ Error: Root element should be 'odoo', found '{root.tag}'")
            return False
        
        # Check for required elements
        report_action = root.find(".//record[@id='action_sla_performance_report']")
        if report_action is None:
            print("❌ Error: Missing report action record")
            return False
        
        template = root.find(".//template[@id='sla_performance_report']")
        if template is None:
            print("❌ Error: Missing report template")
            return False
        
        # Check for required fields in the report action
        required_fields = ['name', 'model', 'report_type', 'report_name', 'report_file']
        for field in required_fields:
            field_elem = report_action.find(f"field[@name='{field}']")
            if field_elem is None:
                print(f"❌ Error: Missing required field '{field}' in report action")
                return False
        
        print("✅ SLA performance report XML file is syntactically correct")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_manifest_inclusion():
    """Test that the SLA performance report is included in the manifest"""
    
    manifest_path = "odoo17/addons/facilities_management/__manifest__.py"
    
    if not os.path.exists(manifest_path):
        print(f"❌ Error: Manifest file {manifest_path} does not exist")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        if "'reports/sla_performance_report.xml'" in content:
            print("✅ SLA performance report is included in the manifest")
            return True
        else:
            print("❌ Error: SLA performance report is not included in the manifest")
            return False
            
    except Exception as e:
        print(f"❌ Error reading manifest file: {e}")
        return False

def test_sla_model_fix():
    """Test that the SLA model has been fixed"""
    
    sla_model_path = "odoo17/addons/facilities_management/models/sla.py"
    
    if not os.path.exists(sla_model_path):
        print(f"❌ Error: SLA model file {sla_model_path} does not exist")
        return False
    
    try:
        with open(sla_model_path, 'r') as f:
            content = f.read()
        
        # Check for the fixed action_export_report method
        if "doc_ids" in content and "doc_model" in content:
            print("✅ SLA model has been fixed with proper report action")
            return True
        else:
            print("❌ Error: SLA model has not been properly fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error reading SLA model file: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing SLA performance report fix...")
    print("=" * 50)
    
    tests = [
        ("XML Syntax", test_xml_syntax),
        ("Manifest Inclusion", test_manifest_inclusion),
        ("SLA Model Fix", test_sla_model_fix),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The SLA performance report fix should resolve the error.")
        print("\nSummary of changes made:")
        print("1. Created odoo17/addons/facilities_management/reports/sla_performance_report.xml")
        print("2. Updated odoo17/addons/facilities_management/__manifest__.py to include the new report")
        print("3. Fixed the action_export_report method in the SLA model")
        print("\nThe error 'External ID not found in the system: facilities_management.sla_performance_report' should now be resolved.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()