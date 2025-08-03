#!/usr/bin/env python3
"""
Test script to verify the ESG template fix
"""

import os
import sys

def find_matching_closing_tag(content, start_pos):
    """Find the matching closing tag for a conditional block"""
    # Find the opening tag
    opening_tag_start = content.find("<t t-if=", start_pos)
    if opening_tag_start == -1:
        return -1
    
    # Find the end of the opening tag
    opening_tag_end = content.find(">", opening_tag_start)
    if opening_tag_end == -1:
        return -1
    
    # Start searching for the closing tag after the opening tag
    pos = opening_tag_end + 1
    depth = 1  # We're already inside one level
    
    while pos < len(content):
        # Look for opening tags
        next_open = content.find("<t t-if=", pos)
        # Look for closing tags
        next_close = content.find("</t>", pos)
        
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            # Found another opening tag
            depth += 1
            pos = next_open + 1
        elif next_close != -1:
            # Found a closing tag
            depth -= 1
            if depth == 0:
                # This is the matching closing tag
                return next_close
            pos = next_close + 1
        else:
            # No more tags found
            break
    
    return -1

def test_template_fix():
    """Test if the template fix is working correctly"""
    
    # Check if the template file exists
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    if not os.path.exists(template_file):
        print("❌ Template file not found:", template_file)
        return False
    
    # Read the template file
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Check for the problematic line that was causing the error
    problematic_line = "<t t-esc=\"'Yes' if o else 'No'\"/>"
    
    if problematic_line in content:
        print("❌ Found problematic line in template")
        print("   Line:", problematic_line)
        return False
    
    # Check if the fix is in place
    fixed_line = "<p><strong>Wizard object exists:</strong> Yes</p>"
    
    if fixed_line in content:
        print("✅ Found fixed line in template")
    else:
        print("❌ Fixed line not found in template")
        return False
    
    # Check if the conditional structure is correct
    if "<t t-if=\"o and o.id\">" in content:
        print("✅ Found main conditional block")
    else:
        print("❌ Main conditional block not found")
        return False
    
    # Check if the else clause is present
    if "<t t-else=\"\">" in content:
        print("✅ Found else clause for when o is None")
    else:
        print("❌ Else clause not found")
        return False
    
    # Find the position of the main conditional block
    main_conditional_start = content.find("<t t-if=\"o and o.id\">")
    main_conditional_end = find_matching_closing_tag(content, main_conditional_start)
    
    if main_conditional_start == -1 or main_conditional_end == -1:
        print("❌ Could not find main conditional block boundaries")
        return False
    
    print(f"Main conditional block: {main_conditional_start} to {main_conditional_end}")
    
    # Check if all sections that reference 'o' are inside the main conditional block
    sections_to_check = [
        "o.include_section_environmental",
        "o.include_section_social", 
        "o.include_section_governance",
        "o.include_section_analytics",
        "o.include_section_recommendations",
        "o.include_thresholds",
        "o.report_theme",
        "o.include_charts",
        "o.include_executive_summary",
        "o.include_recommendations",
        "o.include_benchmarks",
        "o.include_risk_analysis",
        "o.include_trends",
        "o.include_forecasting"
    ]
    
    # Check if all sections are inside the main conditional block
    conditional_content = content[main_conditional_start:main_conditional_end]
    
    for section in sections_to_check:
        if section in content:
            if section in conditional_content:
                print(f"✅ Section '{section}' is inside main conditional block")
            else:
                print(f"❌ Section '{section}' is outside main conditional block")
                # Find where this section is located
                section_pos = content.find(section)
                if section_pos != -1:
                    print(f"   Section found at position: {section_pos}")
                    # Check if it's before or after the main conditional block
                    if section_pos < main_conditional_start:
                        print(f"   Section is BEFORE the main conditional block")
                    elif section_pos > main_conditional_end:
                        print(f"   Section is AFTER the main conditional block")
                    else:
                        print(f"   Section should be inside but wasn't found in conditional content")
                return False
    
    print("✅ All sections that reference 'o' are inside the main conditional block")
    
    # Check for proper error handling
    if "No Data Available" in content:
        print("✅ Found error handling for when o is None")
    else:
        print("❌ Error handling for None o not found")
        return False
    
    print("\n🎉 Template fix verification completed successfully!")
    print("The template should now handle None values properly without throwing TypeError.")
    
    return True

if __name__ == "__main__":
    success = test_template_fix()
    sys.exit(0 if success else 1)