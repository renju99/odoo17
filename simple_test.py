#!/usr/bin/env python3

import os
import re

def check_model_fix():
    """Check if the model fix is correctly implemented"""
    
    print("🔍 Checking model fix implementation...")
    
    # Check if the ESG wizard uses the correct model name
    esg_wizard_path = "/workspace/odoo17/addons/esg_reporting/wizard/esg_report_wizard.py"
    
    if os.path.exists(esg_wizard_path):
        with open(esg_wizard_path, 'r') as f:
            content = f.read()
            
        # Check if the correct model name is used
        if "self.env['facilities.asset']" in content:
            print("✅ SUCCESS: ESG wizard uses correct model name 'facilities.asset'")
        else:
            print("❌ ERROR: ESG wizard still uses incorrect model name")
            
        # Check if esg_compliance field is referenced
        if "esg_compliance" in content:
            print("✅ SUCCESS: ESG wizard references esg_compliance field")
        else:
            print("❌ ERROR: ESG wizard doesn't reference esg_compliance field")
            
        # Check if carbon_footprint field is referenced
        if "carbon_footprint" in content:
            print("✅ SUCCESS: ESG wizard references carbon_footprint field")
        else:
            print("❌ ERROR: ESG wizard doesn't reference carbon_footprint field")
    else:
        print("❌ ERROR: ESG wizard file not found")
    
    # Check if the asset model has the required ESG fields
    asset_model_path = "/workspace/odoo17/addons/facilities_management/models/asset.py"
    
    if os.path.exists(asset_model_path):
        with open(asset_model_path, 'r') as f:
            content = f.read()
            
        # Check if ESG fields are defined
        esg_fields = [
            'esg_compliance',
            'carbon_footprint',
            'energy_efficiency_rating',
            'renewable_energy_usage',
            'waste_management_score',
            'water_consumption',
            'biodiversity_impact',
            'community_impact_score',
            'employee_satisfaction',
            'diversity_index',
            'health_safety_score',
            'training_hours',
            'local_procurement',
            'compliance_rate',
            'risk_management_score',
            'transparency_index',
            'board_diversity',
            'ethics_score',
            'stakeholder_engagement'
        ]
        
        missing_fields = []
        for field in esg_fields:
            if field not in content:
                missing_fields.append(field)
        
        if not missing_fields:
            print("✅ SUCCESS: All ESG fields are defined in asset model")
        else:
            print(f"❌ ERROR: Missing ESG fields: {missing_fields}")
            
        # Check if the model name is correct
        if "_name = 'facilities.asset'" in content:
            print("✅ SUCCESS: Asset model has correct name 'facilities.asset'")
        else:
            print("❌ ERROR: Asset model has incorrect name")
    else:
        print("❌ ERROR: Asset model file not found")
    
    # Check if the views include ESG fields
    asset_views_path = "/workspace/odoo17/addons/facilities_management/views/facility_asset_views.xml"
    
    if os.path.exists(asset_views_path):
        with open(asset_views_path, 'r') as f:
            content = f.read()
            
        # Check if ESG page exists
        if 'string="ESG Metrics"' in content:
            print("✅ SUCCESS: ESG Metrics page exists in asset views")
        else:
            print("❌ ERROR: ESG Metrics page missing from asset views")
            
        # Check if ESG fields are in the tree view
        if 'esg_compliance' in content and 'carbon_footprint' in content:
            print("✅ SUCCESS: ESG fields included in asset views")
        else:
            print("❌ ERROR: ESG fields missing from asset views")
    else:
        print("❌ ERROR: Asset views file not found")

if __name__ == "__main__":
    check_model_fix()