#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import re
import sys

def check_qweb_structure(file_path):
    """Check QWeb template structure for common issues."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        issues = []
        
        # Check for t-if, t-else, t-elif directives
        for elem in root.iter():
            # Check for t-else without proper t-if structure
            if 't-else' in elem.attrib:
                # Check if this element has a proper t-if sibling
                parent = elem
                while parent is not None:
                    parent = parent.getparent()
                    if parent is not None:
                        siblings = list(parent)
                        current_index = siblings.index(elem)
                        
                        # Look for t-if before this t-else
                        found_t_if = False
                        for i in range(current_index - 1, -1, -1):
                            if 't-if' in siblings[i].attrib:
                                found_t_if = True
                                break
                            elif 't-elif' in siblings[i].attrib:
                                found_t_if = True
                                break
                            elif 't-else' in siblings[i].attrib:
                                # Found another t-else, which is fine
                                break
                        
                        if not found_t_if:
                            issues.append(f"t-else directive without preceding t-if or t-elif")
                        break
            
            # Check for t-elif without proper t-if structure
            if 't-elif' in elem.attrib:
                parent = elem
                while parent is not None:
                    parent = parent.getparent()
                    if parent is not None:
                        siblings = list(parent)
                        current_index = siblings.index(elem)
                        
                        # Look for t-if or t-elif before this t-elif
                        found_t_if = False
                        for i in range(current_index - 1, -1, -1):
                            if 't-if' in siblings[i].attrib:
                                found_t_if = True
                                break
                            elif 't-elif' in siblings[i].attrib:
                                found_t_if = True
                                break
                            elif 't-else' in siblings[i].attrib:
                                # Found t-else, which means no t-if before
                                break
                        
                        if not found_t_if:
                            issues.append(f"t-elif directive without preceding t-if or t-elif")
                        break
        
        if issues:
            print(f"✗ {file_path} - Found {len(issues)} QWeb structure issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"✓ {file_path} - QWeb structure is valid")
            return True
            
    except Exception as e:
        print(f"✗ {file_path} - Error: {e}")
        return False

def main():
    # Check the ESG report templates file
    esg_template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    print("Validating QWeb Template Structure...")
    success = check_qweb_structure(esg_template_file)
    
    if success:
        print("\n✓ All QWeb templates have valid structure!")
        return 0
    else:
        print("\n✗ QWeb structure validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())