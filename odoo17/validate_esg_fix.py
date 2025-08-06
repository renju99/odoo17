#!/usr/bin/env python3
"""
ESG Module Field Validation Script
This script validates that the enhanced.esg.wizard model fields are properly defined
and can help diagnose field-related issues during module upgrades.
"""

import ast
import xml.etree.ElementTree as ET
import os
import sys

def validate_python_model(file_path):
    """Validate the Python model definition"""
    print("=== Python Model Validation ===")
    
    if not os.path.exists(file_path):
        print(f"❌ Model file not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Find EnhancedESGWizard class
        enhanced_wizard_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'EnhancedESGWizard':
                enhanced_wizard_class = node
                break
        
        if not enhanced_wizard_class:
            print("❌ EnhancedESGWizard class not found")
            return False
        
        print("✅ EnhancedESGWizard class found")
        
        # Check _name attribute
        has_name = False
        fields_found = []
        
        for item in enhanced_wizard_class.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '_name':
                            if (isinstance(item.value, ast.Str) and 
                                item.value.s == 'enhanced.esg.wizard'):
                                has_name = True
                                print("✅ Model _name correctly set to 'enhanced.esg.wizard'")
                        elif target.id.startswith('include_'):
                            fields_found.append(target.id)
        
        if not has_name:
            print("❌ Model _name not properly set")
            return False
        
        # Check critical fields
        critical_fields = [
            'include_recommendations', 'include_charts', 'include_executive_summary',
            'include_benchmarks', 'include_risk_analysis', 'include_trends'
        ]
        
        missing_fields = []
        for field in critical_fields:
            if field in fields_found:
                print(f"✅ Field '{field}' found")
            else:
                print(f"❌ Field '{field}' missing")
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        print("✅ All critical fields found")
        return True
        
    except Exception as e:
        print(f"❌ Error parsing Python model: {e}")
        return False

def validate_xml_view(file_path):
    """Validate the XML view definition"""
    print("\n=== XML View Validation ===")
    
    if not os.path.exists(file_path):
        print(f"❌ View file not found: {file_path}")
        return False
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Check XML structure
        print("✅ XML syntax is valid")
        
        # Find the enhanced ESG wizard view
        wizard_view = None
        for record in root.findall('.//record[@id="view_enhanced_esg_wizard_form"]'):
            wizard_view = record
            break
        
        if wizard_view is None:
            print("❌ Enhanced ESG wizard view not found")
            return False
        
        print("✅ Enhanced ESG wizard view found")
        
        # Check model reference
        model_field = wizard_view.find('.//field[@name="model"]')
        if model_field is not None and model_field.text == 'enhanced.esg.wizard':
            print("✅ View model correctly references 'enhanced.esg.wizard'")
        else:
            print("❌ View model reference incorrect")
            return False
        
        # Check field references
        critical_fields = [
            'include_recommendations', 'include_charts', 'include_executive_summary',
            'include_benchmarks', 'include_risk_analysis', 'include_trends'
        ]
        
        missing_field_refs = []
        for field in critical_fields:
            field_elem = root.find(f'.//field[@name="{field}"]')
            if field_elem is not None:
                print(f"✅ Field reference '{field}' found in view")
            else:
                print(f"❌ Field reference '{field}' missing in view")
                missing_field_refs.append(field)
        
        if missing_field_refs:
            print(f"❌ Missing field references: {missing_field_refs}")
            return False
        
        print("✅ All critical field references found")
        return True
        
    except Exception as e:
        print(f"❌ Error parsing XML view: {e}")
        return False

def validate_manifest(file_path):
    """Validate the manifest file"""
    print("\n=== Manifest Validation ===")
    
    if not os.path.exists(file_path):
        print(f"❌ Manifest file not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if view file is included in data
        if 'enhanced_esg_wizard_views.xml' in content:
            print("✅ Enhanced ESG wizard view included in manifest data")
        else:
            print("❌ Enhanced ESG wizard view not included in manifest data")
            return False
        
        # Check dependencies
        required_deps = ['base', 'web']
        for dep in required_deps:
            if f"'{dep}'" in content or f'"{dep}"' in content:
                print(f"✅ Required dependency '{dep}' found")
            else:
                print(f"⚠️ Required dependency '{dep}' may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def main():
    """Main validation function"""
    base_path = "/home/runner/work/odoo17/odoo17/odoo17/addons/esg_reporting"
    
    # File paths
    model_file = os.path.join(base_path, "wizard", "esg_report_wizard.py")
    view_file = os.path.join(base_path, "views", "enhanced_esg_wizard_views.xml")
    manifest_file = os.path.join(base_path, "__manifest__.py")
    
    print("ESG Module Field Validation")
    print("=" * 50)
    
    # Run validations
    model_valid = validate_python_model(model_file)
    view_valid = validate_xml_view(view_file)
    manifest_valid = validate_manifest(manifest_file)
    
    # Summary
    print("\n=== Validation Summary ===")
    all_valid = model_valid and view_valid and manifest_valid
    
    if all_valid:
        print("🎉 All validations passed!")
        print("\nThe field definition issue should be resolved.")
        print("If you still encounter the error, try:")
        print("1. Module upgrade: ./odoo-bin -d your_db -u esg_reporting")
        print("2. Module reinstall: ./odoo-bin -d your_db -i esg_reporting")
    else:
        print("❌ Some validations failed!")
        print("Please fix the issues above before upgrading the module.")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())