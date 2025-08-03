#!/usr/bin/env python3
import re
import sys

def check_qweb_structure(file_path):
    """Check QWeb template structure for the specific issue we fixed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the specific pattern that was causing the issue
        # Look for t-else="" that might not be properly structured
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for t-else="" without proper t-if structure
            if 't-else=""' in line:
                # Look for t-if before this line in the same context
                found_t_if = False
                for j in range(i-1, max(0, i-50), -1):  # Look back up to 50 lines
                    if 't-if=' in lines[j]:
                        found_t_if = True
                        break
                    elif 't-elif=' in lines[j]:
                        found_t_if = True
                        break
                    elif 't-else=""' in lines[j] and j != i:
                        # Found another t-else, which is fine
                        break
                    elif '</t>' in lines[j]:
                        # Check if this closes a t-if block
                        # Look for the opening t-if
                        for k in range(j-1, max(0, j-20), -1):
                            if 't-if=' in lines[k]:
                                found_t_if = True
                                break
                            elif 't-elif=' in lines[k]:
                                found_t_if = True
                                break
                            elif '<t ' in lines[k] and 't-else=""' not in lines[k]:
                                # Found another t element, stop looking
                                break
                        if found_t_if:
                            break
                
                if not found_t_if:
                    issues.append(f"Line {i}: t-else directive without preceding t-if or t-elif")
        
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