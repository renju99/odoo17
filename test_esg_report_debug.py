#!/usr/bin/env python3
"""
Debug script to test ESG report generation
"""

import os
import sys

def test_esg_report_data():
    """Test ESG report data generation"""
    
    print("🔍 Testing ESG Report Data Generation...")
    
    # Check if the wizard file exists
    wizard_file = "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    if not os.path.exists(wizard_file):
        print("❌ ERROR: Wizard file not found")
        return False
    
    with open(wizard_file, 'r') as f:
        content = f.read()
    
    # Check the domain logic
    print("\n📋 Domain Logic Analysis:")
    
    # Check if the domain is too restrictive
    if "('purchase_date', '>=', self.date_from)" in content:
        print("✅ SUCCESS: Date range filter is implemented")
    else:
        print("❌ ERROR: Date range filter missing")
    
    if "('purchase_date', '<=', self.date_to)" in content:
        print("✅ SUCCESS: Date range filter is implemented")
    else:
        print("❌ ERROR: Date range filter missing")
    
    # Check if there's a fallback for when no assets are found
    if "if not assets:" in content or "if len(assets) == 0:" in content:
        print("✅ SUCCESS: Empty assets handling found")
    else:
        print("❌ WARNING: No empty assets handling found")
    
    # Check if the report data preparation handles empty assets
    if "_prepare_enhanced_report_data" in content:
        print("✅ SUCCESS: Report data preparation method exists")
    else:
        print("❌ ERROR: Report data preparation method missing")
    
    print("\n💡 SUGGESTIONS:")
    print("1. The domain might be too restrictive - try removing date filters")
    print("2. Add fallback data when no assets are found")
    print("3. Check if assets exist in the database")
    print("4. Verify the date range is reasonable")
    
    return True

def test_template_data():
    """Test template data structure"""
    
    print("\n🔍 Testing Template Data Structure...")
    
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    if not os.path.exists(template_file):
        print("❌ ERROR: Template file not found")
        return False
    
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Check if the template expects specific data
    if "o.report_name" in content:
        print("✅ SUCCESS: Template expects report_name")
    else:
        print("❌ ERROR: Template missing report_name reference")
    
    if "o.report_type" in content:
        print("✅ SUCCESS: Template expects report_type")
    else:
        print("❌ ERROR: Template missing report_type reference")
    
    if "o.date_from" in content:
        print("✅ SUCCESS: Template expects date_from")
    else:
        print("❌ ERROR: Template missing date_from reference")
    
    if "o.date_to" in content:
        print("✅ SUCCESS: Template expects date_to")
    else:
        print("❌ ERROR: Template missing date_to reference")
    
    return True

def main():
    print("Testing ESG Report Debug...")
    print("=" * 50)
    
    test_esg_report_data()
    test_template_data()
    
    print("\n🎯 RECOMMENDED FIXES:")
    print("1. Modify the domain to be less restrictive:")
    print("   - Remove date filters initially")
    print("   - Add fallback data when no assets found")
    print("2. Add debug logging to see what data is being passed")
    print("3. Test with a wider date range")
    print("4. Ensure demo data is loaded")

if __name__ == "__main__":
    main()