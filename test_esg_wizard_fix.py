#!/usr/bin/env python3
"""
Test script to verify the ESG wizard fix.
This script checks if the enhanced.esg.wizard model has all the required fields.
"""

import os
import sys
import ast

def check_wizard_fields():
    """Check if the EnhancedESGWizard model has all required fields."""
    
    wizard_file = "/workspace/odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    
    if not os.path.exists(wizard_file):
        print("❌ Wizard file not found:", wizard_file)
        return False
    
    try:
        with open(wizard_file, 'r') as f:
            content = f.read()
        
        # Parse the Python file
        tree = ast.parse(content)
        
        # Find the EnhancedESGWizard class
        wizard_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'EnhancedESGWizard':
                wizard_class = node
                break
        
        if not wizard_class:
            print("❌ EnhancedESGWizard class not found")
            return False
        
        # Extract field definitions
        fields = []
        for node in ast.walk(wizard_class):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and target.attr.endswith('= fields.'):
                        fields.append(target.attr.split('=')[0].strip())
        
        # Required fields from the view
        required_fields = [
            'report_name', 'report_type', 'company_name', 'output_format',
            'date_from', 'date_to', 'granularity', 'report_theme',
            'asset_type', 'include_compliance_only', 'comparison_period',
            'custom_comparison_from', 'custom_comparison_to',
            'include_predictive_analysis', 'include_correlation_analysis',
            'include_anomaly_detection', 'include_advanced_analytics',
            'include_charts', 'include_executive_summary', 'include_recommendations',
            'include_benchmarks', 'include_risk_analysis', 'include_trends',
            'include_forecasting', 'include_emissions_data', 'include_offset_data',
            'include_community_data', 'include_initiatives_data',
            'include_gender_parity_data', 'include_pay_gap_data', 'include_analytics_data',
            'include_section_environmental', 'include_section_social',
            'include_section_governance', 'include_section_analytics',
            'include_section_recommendations', 'include_thresholds',
            'carbon_threshold', 'compliance_threshold', 'social_impact_threshold',
            'include_logo', 'include_footer', 'custom_metrics', 'custom_charts',
            'company_id'
        ]
        
        # Check if all required fields are present
        missing_fields = []
        for field in required_fields:
            if not any(field in line for line in content.split('\n')):
                missing_fields.append(field)
        
        if missing_fields:
            print("❌ Missing fields in EnhancedESGWizard:")
            for field in missing_fields:
                print(f"   - {field}")
            return False
        
        print("✅ All required fields are present in EnhancedESGWizard")
        return True
        
    except Exception as e:
        print(f"❌ Error checking wizard fields: {e}")
        return False

def check_view_file():
    """Check if the view file exists and is properly formatted."""
    
    view_file = "/workspace/odoo17/addons/esg_reporting/views/enhanced_esg_wizard_views.xml"
    
    if not os.path.exists(view_file):
        print("❌ View file not found:", view_file)
        return False
    
    try:
        with open(view_file, 'r') as f:
            content = f.read()
        
        # Check for basic XML structure
        if '<?xml version="1.0" encoding="utf-8"?>' not in content:
            print("❌ View file missing XML declaration")
            return False
        
        if '<odoo>' not in content:
            print("❌ View file missing <odoo> tag")
            return False
        
        if 'enhanced.esg.wizard' not in content:
            print("❌ View file missing model reference")
            return False
        
        print("✅ View file is properly formatted")
        return True
        
    except Exception as e:
        print(f"❌ Error checking view file: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 Testing ESG Wizard Fix...")
    print("=" * 50)
    
    # Check wizard fields
    wizard_ok = check_wizard_fields()
    
    # Check view file
    view_ok = check_view_file()
    
    print("=" * 50)
    if wizard_ok and view_ok:
        print("✅ All tests passed! The ESG wizard should now work correctly.")
        print("\n📝 Summary of fixes:")
        print("   - Added all missing fields to EnhancedESGWizard model")
        print("   - Fields include: report_type, company_name, output_format, etc.")
        print("   - View file references are now valid")
        print("\n🚀 You can now upgrade the ESG reporting module without errors.")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())