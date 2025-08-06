#!/usr/bin/env python3
"""
Test script for ESG Report functionality
"""

import sys
import os

# Add the facilities_management_module to the path
sys.path.insert(0, '/workspace/facilities_management_module')

def test_esg_report_imports():
    """Test that all ESG report modules can be imported"""
    try:
        from models.asset import Asset
        print("✓ Asset model imported successfully")
        
        from models.asset_certification import AssetCertification
        print("✓ AssetCertification model imported successfully")
        
        from wizard.esg_report_wizard import ESGReportWizard
        print("✓ ESGReportWizard imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_esg_report_structure():
    """Test the structure of ESG report components"""
    try:
        # Check if required files exist
        required_files = [
            'facilities_management_module/models/asset.py',
            'facilities_management_module/models/asset_certification.py',
            'facilities_management_module/wizard/esg_report_wizard.py',
            'facilities_management_module/views/esg_report_wizard_views.xml',
            'facilities_management_module/views/asset_certification_views.xml',
            'facilities_management_module/views/esg_report_menus.xml',
            'facilities_management_module/reports/esg_report_pdf.xml',
            'facilities_management_module/demo/esg_demo_data.xml',
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✓ {file_path} exists")
            else:
                print(f"✗ {file_path} missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking file structure: {e}")
        return False

def test_manifest_includes():
    """Test that manifest includes all ESG components"""
    try:
        with open('facilities_management_module/__manifest__.py', 'r') as f:
            manifest_content = f.read()
        
        required_includes = [
            'views/asset_certification_views.xml',
            'views/esg_report_wizard_views.xml',
            'views/esg_report_menus.xml',
            'reports/esg_report_pdf.xml',
            'demo/esg_demo_data.xml',
        ]
        
        for include in required_includes:
            if include in manifest_content:
                print(f"✓ {include} included in manifest")
            else:
                print(f"✗ {include} missing from manifest")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking manifest: {e}")
        return False

def main():
    """Run all ESG report tests"""
    print("Testing ESG Report Functionality")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_esg_report_imports),
        ("File Structure Tests", test_esg_report_structure),
        ("Manifest Tests", test_manifest_includes),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        if test_func():
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All ESG report tests passed!")
        print("\nTo use the ESG report functionality:")
        print("1. Install the facilities_management_module in Odoo")
        print("2. Navigate to Assets > ESG Reports > Generate ESG Report")
        print("3. Configure your report parameters and generate the report")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)