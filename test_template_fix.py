#!/usr/bin/env python3
"""
Test script to verify the ESG reporting template fix.
This script tests that the template no longer contains forbidden __name__ access.
"""

import re
import sys
from pathlib import Path

def check_template_security(template_path):
    """Check if the template contains any forbidden patterns."""
    forbidden_patterns = [
        r'\.__name__',  # Access to __name__ attribute
        r'\.__[a-zA-Z_]+__',  # Any dunder method access
        r'__import__',  # Import function
        r'eval\s*\(',  # Eval function
        r'exec\s*\(',  # Exec function
        r'globals\s*\(',  # Globals function
        r'locals\s*\(',  # Locals function
    ]
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        for pattern in forbidden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(f"Line {line_num}: {match.group()}")
        
        if issues:
            print(f"❌ Security issues found in {template_path}:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"✅ No security issues found in {template_path}")
            return True
            
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error checking template: {e}")
        return False

def main():
    """Main function to test the template fix."""
    template_path = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    print("Testing ESG reporting template security...")
    print("=" * 50)
    
    success = check_template_security(template_path)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Template security check passed!")
        print("The __name__ access issue has been fixed.")
        print("The template should now compile without security errors.")
    else:
        print("❌ Template security check failed!")
        print("Please review and fix the identified issues.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())