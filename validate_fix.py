#!/usr/bin/env python3
"""
Validation script to check if the facilities_management module fix is correct.
This script validates that:
1. The maintenance_workorder_views.xml file exists and is properly structured
2. All referenced views in facility_asset_menus.xml exist
3. The manifest includes the missing view file
"""

import os
import xml.etree.ElementTree as ET
import re

def check_file_exists(filepath):
    """Check if a file exists."""
    return os.path.exists(filepath)

def parse_xml_file(filepath):
    """Parse XML file and return root element."""
    try:
        tree = ET.parse(filepath)
        return tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {filepath}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None

def find_view_ids(xml_root):
    """Find all view IDs in an XML file."""
    view_ids = []
    if xml_root is None:
        return view_ids
    
    for record in xml_root.findall(".//record"):
        record_id = record.get('id')
        if record_id:
            view_ids.append(record_id)
    
    return view_ids

def find_ref_references(xml_root):
    """Find all ref() references in an XML file."""
    refs = []
    if xml_root is None:
        return refs
    
    # Convert to string and use regex to find ref() calls
    xml_str = ET.tostring(xml_root, encoding='unicode')
    ref_pattern = r"ref\('([^']+)'\)"
    matches = re.findall(ref_pattern, xml_str)
    refs.extend(matches)
    
    return refs

def check_manifest_includes_file(manifest_path, filename):
    """Check if manifest includes a specific file."""
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
            return filename in content
    except FileNotFoundError:
        print(f"Manifest file not found: {manifest_path}")
        return False

def main():
    print("=== Facilities Management Module Fix Validation ===\n")
    
    # File paths
    base_path = "odoo17/addons/facilities_management"
    manifest_path = f"{base_path}/__manifest__.py"
    menus_file = f"{base_path}/views/facility_asset_menus.xml"
    workorder_views_file = f"{base_path}/views/maintenance_workorder_views.xml"
    kanban_views_file = f"{base_path}/views/maintenance_workorder_kanban.xml"
    
    # Check 1: Does maintenance_workorder_views.xml exist?
    print("1. Checking if maintenance_workorder_views.xml exists...")
    if check_file_exists(workorder_views_file):
        print("   ✓ maintenance_workorder_views.xml exists")
    else:
        print("   ✗ maintenance_workorder_views.xml not found")
        return False
    
    # Check 2: Does the manifest include the workorder views file?
    print("\n2. Checking if manifest includes maintenance_workorder_views.xml...")
    if check_manifest_includes_file(manifest_path, "maintenance_workorder_views.xml"):
        print("   ✓ maintenance_workorder_views.xml is included in manifest")
    else:
        print("   ✗ maintenance_workorder_views.xml is NOT included in manifest")
        return False
    
    # Check 3: Parse the workorder views file and find view IDs
    print("\n3. Checking views in maintenance_workorder_views.xml...")
    workorder_root = parse_xml_file(workorder_views_file)
    if workorder_root is not None:
        view_ids = find_view_ids(workorder_root)
        print(f"   Found {len(view_ids)} views:")
        for view_id in view_ids:
            print(f"     - {view_id}")
        
        # Check for specific required views
        required_views = ['view_workorder_form', 'view_maintenance_workorder_tree']
        missing_views = [view for view in required_views if view not in view_ids]
        if missing_views:
            print(f"   ✗ Missing required views: {missing_views}")
            return False
        else:
            print("   ✓ All required views found")
    else:
        print("   ✗ Could not parse maintenance_workorder_views.xml")
        return False
    
    # Check 4: Parse the kanban views file
    print("\n4. Checking views in maintenance_workorder_kanban.xml...")
    kanban_root = parse_xml_file(kanban_views_file)
    if kanban_root is not None:
        kanban_view_ids = find_view_ids(kanban_root)
        print(f"   Found {len(kanban_view_ids)} views:")
        for view_id in kanban_view_ids:
            print(f"     - {view_id}")
        
        if 'view_maintenance_workorder_kanban' in kanban_view_ids:
            print("   ✓ view_maintenance_workorder_kanban found")
        else:
            print("   ✗ view_maintenance_workorder_kanban not found")
            return False
    else:
        print("   ✗ Could not parse maintenance_workorder_kanban.xml")
        return False
    
    # Check 5: Check ref() references in menus file
    print("\n5. Checking ref() references in facility_asset_menus.xml...")
    menus_root = parse_xml_file(menus_file)
    if menus_root is not None:
        refs = find_ref_references(menus_root)
        print(f"   Found {len(refs)} ref() references:")
        for ref in refs:
            print(f"     - {ref}")
        
        # Check for specific required references
        required_refs = [
            'facilities_management.view_maintenance_workorder_kanban',
            'facilities_management.view_maintenance_workorder_tree',
            'facilities_management.view_workorder_form'
        ]
        missing_refs = [ref for ref in required_refs if ref not in refs]
        if missing_refs:
            print(f"   ✗ Missing required references: {missing_refs}")
            return False
        else:
            print("   ✓ All required references found")
    else:
        print("   ✗ Could not parse facility_asset_menus.xml")
        return False
    
    print("\n=== VALIDATION COMPLETE ===")
    print("✓ All checks passed! The fix should resolve the error.")
    print("\nThe issue was that 'maintenance_workorder_views.xml' was not included")
    print("in the manifest's data section, but 'facility_asset_menus.xml' was")
    print("trying to reference views from it. Adding the file to the manifest")
    print("should resolve the 'External ID not found' error.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)