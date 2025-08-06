#!/usr/bin/env python3
"""
Test script to verify the ESG reporting module manifest fix
"""

import os
import ast

def test_manifest_file():
    """Test that the manifest file doesn't reference missing files"""
    manifest_path = "odoo17/addons/esg_reporting/__manifest__.py"
    
    if not os.path.exists(manifest_path):
        print(f"❌ Manifest file not found: {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Parse the manifest as a Python dict
        manifest_dict = ast.literal_eval(content)
        
        # Check if the problematic file reference is removed
        data_files = manifest_dict.get('data', [])
        
        problematic_file = 'views/esg_report_wizard_views.xml'
        if problematic_file in data_files:
            print(f"❌ Manifest still references missing file: {problematic_file}")
            return False
        
        # Check if the correct file is referenced
        correct_file = 'views/enhanced_esg_wizard_views.xml'
        if correct_file in data_files:
            print(f"✅ Manifest correctly references: {correct_file}")
        else:
            print(f"❌ Manifest missing correct file: {correct_file}")
            return False
        
        # Check if all referenced files exist
        views_dir = "odoo17/addons/esg_reporting/views"
        for file_path in data_files:
            if file_path.startswith('views/'):
                full_path = f"odoo17/addons/esg_reporting/{file_path}"
                if not os.path.exists(full_path):
                    print(f"❌ Referenced file does not exist: {full_path}")
                    return False
                else:
                    print(f"✅ File exists: {full_path}")
        
        print("✅ All manifest file references are valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing manifest: {e}")
        return False

def test_module_structure():
    """Test that the module structure is correct"""
    module_path = "odoo17/addons/esg_reporting"
    
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'wizard/__init__.py',
        'wizard/esg_report_wizard.py',
        'views/enhanced_esg_wizard_views.xml',
        'security/esg_security.xml',
        'security/ir.model.access.csv',
        'data/esg_data.xml',
        'data/esg_demo.xml',
        'report/esg_reports.xml',
        'report/esg_report_templates.xml'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = f"{module_path}/{file_path}"
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required module files exist!")
    return True

if __name__ == "__main__":
    print("Testing ESG Reporting Module Fix...")
    print("=" * 50)
    
    manifest_ok = test_manifest_file()
    structure_ok = test_module_structure()
    
    print("=" * 50)
    if manifest_ok and structure_ok:
        print("🎉 All tests passed! The module should now load correctly.")
    else:
        print("❌ Some tests failed. Please check the issues above.")