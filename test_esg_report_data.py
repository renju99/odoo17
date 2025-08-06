#!/usr/bin/env python3
"""
Test script to check ESG report wizard functionality and data flow
"""

import sys
import os

# Add the Odoo path
sys.path.append('/workspace/odoo17')

def test_esg_report_data():
    """Test ESG report data generation"""
    
    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        from odoo.modules.registry import Registry
        
        # Initialize Odoo
        odoo.cli.server.main()
        
        # Get the registry
        registry = Registry('test_db')
        
        with api.Environment.manage():
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                print("🔍 Testing ESG Report Wizard Data Flow")
                print("=" * 50)
                
                # Check if ESG wizard model exists
                if 'enhanced.esg.wizard' in env.registry:
                    print("✅ SUCCESS: enhanced.esg.wizard model exists")
                else:
                    print("❌ ERROR: enhanced.esg.wizard model not found")
                    return
                
                # Check if facilities.asset model exists
                if 'facilities.asset' in env.registry:
                    print("✅ SUCCESS: facilities.asset model exists")
                else:
                    print("❌ ERROR: facilities.asset model not found")
                    return
                
                # Count assets in the system
                asset_model = env['facilities.asset']
                asset_count = asset_model.search_count([])
                print(f"📊 Total assets in system: {asset_count}")
                
                if asset_count == 0:
                    print("⚠️  WARNING: No assets found in the system")
                    print("   This is why the ESG report shows no data")
                    print("   You need to create some assets first")
                    return
                
                # Get some sample assets
                assets = asset_model.search([], limit=5)
                print(f"📋 Sample assets found: {len(assets)}")
                
                for asset in assets:
                    print(f"   - {asset.name} (ID: {asset.id})")
                    print(f"     Carbon Footprint: {asset.carbon_footprint or 'Not set'}")
                    print(f"     ESG Compliant: {asset.esg_compliance}")
                    print(f"     Energy Rating: {asset.energy_efficiency_rating or 'Not set'}")
                
                # Test the ESG wizard
                wizard_model = env['enhanced.esg.wizard']
                
                # Create a test wizard
                wizard_vals = {
                    'report_name': 'Test ESG Report',
                    'report_type': 'sustainability',
                    'date_from': '2024-01-01',
                    'date_to': '2024-12-31',
                    'granularity': 'monthly',
                    'asset_type': 'all',
                    'include_compliance_only': False,
                    'include_section_environmental': True,
                    'include_section_social': True,
                    'include_section_governance': True,
                    'include_section_analytics': True,
                    'include_section_recommendations': True,
                    'output_format': 'pdf',
                    'company_name': 'Test Company'
                }
                
                wizard = wizard_model.create(wizard_vals)
                print(f"✅ SUCCESS: Created test wizard with ID: {wizard.id}")
                
                # Test data preparation
                try:
                    report_data = wizard._prepare_enhanced_report_data(assets)
                    print("✅ SUCCESS: Report data prepared successfully")
                    print(f"   Report data keys: {list(report_data.keys())}")
                    
                    if report_data.get('report_info'):
                        report_info = report_data['report_info']
                        print(f"   Total assets analyzed: {report_info.get('total_assets', 0)}")
                        print(f"   Report note: {report_info.get('note', 'None')}")
                    
                    if report_data.get('environmental_metrics'):
                        env_metrics = report_data['environmental_metrics']
                        print(f"   Environmental metrics: {len(env_metrics)} items")
                        for key, value in env_metrics.items():
                            print(f"     {key}: {value}")
                    
                    if report_data.get('recommendations'):
                        recommendations = report_data['recommendations']
                        print(f"   Recommendations: {len(recommendations)} items")
                        for rec in recommendations:
                            print(f"     {rec.get('category', 'Unknown')}: {rec.get('recommendation', '')}")
                    
                except Exception as e:
                    print(f"❌ ERROR: Failed to prepare report data: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Test the report action
                try:
                    action = wizard.action_generate_enhanced_esg_report()
                    print("✅ SUCCESS: Report action generated successfully")
                    print(f"   Action type: {action.get('type', 'Unknown')}")
                    print(f"   Action data keys: {list(action.keys())}")
                except Exception as e:
                    print(f"❌ ERROR: Failed to generate report action: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
    except Exception as e:
        print(f"❌ ERROR: Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_esg_report_data()