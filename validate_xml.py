#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

def validate_xml_file(file_path):
    """Validate XML syntax of a file."""
    try:
        tree = ET.parse(file_path)
        print(f"✓ {file_path} - XML syntax is valid")
        return True
    except ET.ParseError as e:
        print(f"✗ {file_path} - XML syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path} - Error: {e}")
        return False

def main():
    # Validate the ESG report templates file
    esg_template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    print("Validating ESG Report Templates XML...")
    success = validate_xml_file(esg_template_file)
    
    if success:
        print("\n✓ All XML files are syntactically valid!")
        return 0
    else:
        print("\n✗ XML validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())