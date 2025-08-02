#!/usr/bin/env python3

import sys
import os

# Add the Odoo path to sys.path
sys.path.insert(0, '/workspace/odoo17')

# Set up Odoo environment
os.environ['ODOO_CLI'] = '1'

try:
    import odoo
    from odoo import api, fields, models
    from odoo.modules.registry import Registry
    
    # Initialize Odoo
    odoo.cli.server.main()
    
    # Test if the model exists
    registry = Registry('test_db')
    with registry.cursor() as cr:
        env = api.Environment(cr, 1, {})
        
        # Test if facilities.asset model exists
        if 'facilities.asset' in env.registry:
            print("✅ SUCCESS: facilities.asset model exists")
            
            # Test if ESG fields exist
            asset_model = env['facilities.asset']
            if hasattr(asset_model, 'esg_compliance'):
                print("✅ SUCCESS: esg_compliance field exists")
            else:
                print("❌ ERROR: esg_compliance field missing")
                
            if hasattr(asset_model, 'carbon_footprint'):
                print("✅ SUCCESS: carbon_footprint field exists")
            else:
                print("❌ ERROR: carbon_footprint field missing")
                
        else:
            print("❌ ERROR: facilities.asset model not found")
            
        # Test if esg_reporting can access the model
        if 'esg_reporting' in env.registry:
            print("✅ SUCCESS: esg_reporting module loaded")
        else:
            print("❌ ERROR: esg_reporting module not found")
            
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()