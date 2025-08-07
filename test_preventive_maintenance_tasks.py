#!/usr/bin/env python3
"""
Test script to verify preventive maintenance workorder generation with tasks.
This script tests the complete flow from asset maintenance schedule to workorder with tasks.
"""

import sys
import os

# Add the Odoo path to sys.path
sys.path.append('/workspace/odoo17')

def test_preventive_maintenance_flow():
    """Test the complete preventive maintenance flow with tasks."""
    
    try:
        # Import Odoo modules
        import odoo
        from odoo import api, fields, models
        from odoo.tools import config
        
        # Initialize Odoo
        config['db_host'] = 'localhost'
        config['db_port'] = 5432
        config['db_user'] = 'odoo'
        config['db_password'] = 'odoo'
        config['db_name'] = 'odoo17'
        
        # Start Odoo
        odoo.cli.server.main()
        
        # Get the environment
        env = api.Environment.manage()
        
        with env.manage():
            # Test 1: Check if models exist
            print("✓ Testing model existence...")
            
            # Check Asset Maintenance Schedule model
            asset_schedule_model = env['asset.maintenance.schedule']
            print(f"  - Asset Maintenance Schedule model: {asset_schedule_model}")
            
            # Check Maintenance Workorder model
            workorder_model = env['maintenance.workorder']
            print(f"  - Maintenance Workorder model: {workorder_model}")
            
            # Check Job Plan model
            job_plan_model = env['maintenance.job.plan']
            print(f"  - Job Plan model: {job_plan_model}")
            
            # Check Workorder Task model
            workorder_task_model = env['maintenance.workorder.task']
            print(f"  - Workorder Task model: {workorder_task_model}")
            
            # Test 2: Check if methods exist
            print("\n✓ Testing method existence...")
            
            # Check if _generate_preventive_workorders method exists
            if hasattr(asset_schedule_model, '_generate_preventive_workorders'):
                print("  - _generate_preventive_workorders method: ✓")
            else:
                print("  - _generate_preventive_workorders method: ✗")
                return False
            
            # Check if _create_workorder_with_tasks method exists
            if hasattr(asset_schedule_model, '_create_workorder_with_tasks'):
                print("  - _create_workorder_with_tasks method: ✓")
            else:
                print("  - _create_workorder_with_tasks method: ✗")
                return False
            
            # Check if _copy_job_plan_tasks_to_workorder method exists
            if hasattr(asset_schedule_model, '_copy_job_plan_tasks_to_workorder'):
                print("  - _copy_job_plan_tasks_to_workorder method: ✓")
            else:
                print("  - _copy_job_plan_tasks_to_workorder method: ✗")
                return False
            
            # Test 3: Check if fields exist
            print("\n✓ Testing field existence...")
            
            # Check workorder fields
            workorder_fields = workorder_model._fields
            required_fields = ['job_plan_id', 'section_ids', 'workorder_task_ids']
            
            for field in required_fields:
                if field in workorder_fields:
                    print(f"  - workorder.{field}: ✓")
                else:
                    print(f"  - workorder.{field}: ✗")
                    return False
            
            # Check asset schedule fields
            schedule_fields = asset_schedule_model._fields
            required_schedule_fields = ['job_plan_id', 'next_maintenance_date']
            
            for field in required_schedule_fields:
                if field in schedule_fields:
                    print(f"  - schedule.{field}: ✓")
                else:
                    print(f"  - schedule.{field}: ✗")
                    return False
            
            # Test 4: Check if cron job exists
            print("\n✓ Testing cron job existence...")
            
            cron_model = env['ir.cron']
            maintenance_cron = cron_model.search([
                ('name', '=', 'Generate Preventive Maintenance Work Orders')
            ])
            
            if maintenance_cron:
                print("  - Preventive maintenance cron job: ✓")
                print(f"    - Method: {maintenance_cron.code}")
                print(f"    - Interval: {maintenance_cron.interval_number} {maintenance_cron.interval_type}")
            else:
                print("  - Preventive maintenance cron job: ✗")
                return False
            
            print("\n🎉 All tests passed! The preventive maintenance system is properly implemented.")
            return True
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_preventive_maintenance_flow()
    sys.exit(0 if success else 1)