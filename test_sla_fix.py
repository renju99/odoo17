#!/usr/bin/env python3
"""
Test script to verify SLA model fixes
"""

import sys
import os

# Add the odoo17 directory to the Python path
sys.path.insert(0, '/workspace/odoo17')

def test_sla_model():
    """Test the SLA model to ensure computed fields are properly defined"""
    
    try:
        # Import the SLA model
        from addons.facilities_management.models.sla import FacilitiesSLA
        
        # Check if the computed fields have store=True
        compliance_rate_field = FacilitiesSLA._fields.get('compliance_rate')
        if compliance_rate_field and hasattr(compliance_rate_field, 'store') and compliance_rate_field.store:
            print("✓ compliance_rate field has store=True")
        else:
            print("✗ compliance_rate field does not have store=True")
            return False
        
        # Check other computed fields
        computed_fields = ['total_workorders', 'compliant_workorders', 'breached_workorders', 'avg_mttr']
        for field_name in computed_fields:
            field = FacilitiesSLA._fields.get(field_name)
            if field and hasattr(field, 'store') and field.store:
                print(f"✓ {field_name} field has store=True")
            else:
                print(f"✗ {field_name} field does not have store=True")
                return False
        
        print("✓ All computed fields have store=True")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing SLA model: {e}")
        return False

def test_search_view():
    """Test the search view to ensure it's valid"""
    
    try:
        # Read the search view file
        search_view_path = '/workspace/odoo17/addons/facilities_management/views/sla_views.xml'
        
        if not os.path.exists(search_view_path):
            print(f"✗ Search view file not found: {search_view_path}")
            return False
        
        with open(search_view_path, 'r') as f:
            content = f.read()
        
        # Check if the compliance_rate filter exists
        if 'compliance_rate' in content:
            print("✓ compliance_rate field is used in views")
        else:
            print("✗ compliance_rate field not found in views")
            return False
        
        # Check if the low_compliance filter exists
        if 'low_compliance' in content:
            print("✓ low_compliance filter exists")
        else:
            print("✗ low_compliance filter not found")
            return False
        
        print("✓ Search view looks valid")
        return True
        
    except Exception as e:
        print(f"✗ Error testing search view: {e}")
        return False

def main():
    """Main test function"""
    print("Testing SLA model fixes...")
    print("=" * 50)
    
    # Test the SLA model
    model_ok = test_sla_model()
    print()
    
    # Test the search view
    view_ok = test_search_view()
    print()
    
    if model_ok and view_ok:
        print("✓ All tests passed! The SLA model should now work correctly.")
        print("\nTo apply the fixes:")
        print("1. Update the module: python3 odoo-bin -d your_database -u facilities_management")
        print("2. Restart the Odoo server")
        return True
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)