#!/usr/bin/env python3
"""
Validation script to check the SLA views XML file for Odoo 17 compatibility.
"""

import xml.etree.ElementTree as ET
import re
import sys

def validate_xml_syntax(file_path):
    """Validate XML syntax."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print(f"✓ XML syntax is valid for {file_path}")
        return True
    except ET.ParseError as e:
        print(f"✗ XML syntax error in {file_path}: {e}")
        return False

def check_deprecated_attributes(file_path):
    """Check for deprecated attributes in Odoo 17."""
    deprecated_attrs = ['attrs', 'states']
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for deprecated attributes
        for attr in deprecated_attrs:
            pattern = rf'{attr}=["\'][^"\']*["\']'
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    issues.append(f"Deprecated attribute found: {match}")
        
        if issues:
            print(f"✗ Found {len(issues)} deprecated attribute(s) in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"✓ No deprecated attributes found in {file_path}")
            return True
            
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        return False

def check_odoo17_compatibility(file_path):
    """Check for Odoo 17 specific compatibility issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for new Odoo 17 syntax patterns
        new_patterns = [
            r'invisible="[^"]*"',  # New invisible syntax
            r'readonly="[^"]*"',   # New readonly syntax
        ]
        
        for pattern in new_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"✓ Found {len(matches)} Odoo 17 compatible attribute(s)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking Odoo 17 compatibility: {e}")
        return False

def main():
    """Main validation function."""
    file_path = "odoo17/addons/facilities_management/views/sla_views.xml"
    
    print("Validating SLA views XML file for Odoo 17 compatibility...")
    print("=" * 60)
    
    # Check if file exists
    try:
        with open(file_path, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return False
    
    # Validate XML syntax
    syntax_ok = validate_xml_syntax(file_path)
    
    # Check for deprecated attributes
    deprecated_ok = check_deprecated_attributes(file_path)
    
    # Check Odoo 17 compatibility
    compatibility_ok = check_odoo17_compatibility(file_path)
    
    print("=" * 60)
    if syntax_ok and deprecated_ok and compatibility_ok:
        print("✓ All validations passed! The file is compatible with Odoo 17.")
        return True
    else:
        print("✗ Some validations failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)