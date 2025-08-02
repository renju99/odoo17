#!/usr/bin/env python3

# Test script to verify SLA syntax and field definitions
import ast
import sys
import os

def check_file_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        return False

def check_field_exists(file_path, field_name):
    """Check if a field exists in a Python file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if field_name in content:
            return True
        else:
            return False
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        return False

# Test files
sla_file = "/workspace/odoo17/addons/facilities_management/models/sla.py"
integration_file = "/workspace/odoo17/addons/facilities_management/models/workorder_sla_integration.py"

print("Testing SLA fix...")

# Check syntax
print("\n1. Checking file syntax...")
if check_file_syntax(sla_file):
    print("✓ sla.py has valid syntax")
else:
    print("✗ sla.py has syntax errors")

if check_file_syntax(integration_file):
    print("✓ workorder_sla_integration.py has valid syntax")
else:
    print("✗ workorder_sla_integration.py has syntax errors")

# Check field existence
print("\n2. Checking field definitions...")
if check_field_exists(sla_file, "critical_threshold_hours"):
    print("✓ critical_threshold_hours field exists in sla.py")
else:
    print("✗ critical_threshold_hours field missing in sla.py")

if check_field_exists(sla_file, "warning_threshold_hours"):
    print("✓ warning_threshold_hours field exists in sla.py")
else:
    print("✗ warning_threshold_hours field missing in sla.py")

# Check integration file uses correct field names
print("\n3. Checking integration file field references...")
if check_field_exists(integration_file, "critical_threshold_hours"):
    print("✓ workorder_sla_integration.py references critical_threshold_hours")
else:
    print("✗ workorder_sla_integration.py missing critical_threshold_hours reference")

if check_field_exists(integration_file, "warning_threshold_hours"):
    print("✓ workorder_sla_integration.py references warning_threshold_hours")
else:
    print("✗ workorder_sla_integration.py missing warning_threshold_hours reference")

# Check that old field names are not used
print("\n4. Checking for old field name usage...")
if not check_field_exists(integration_file, "critical_threshold"):
    print("✓ No references to old critical_threshold field")
else:
    print("✗ Found references to old critical_threshold field")

if not check_field_exists(integration_file, "warning_threshold"):
    print("✓ No references to old warning_threshold field")
else:
    print("✗ Found references to old warning_threshold field")

print("\n✓ SLA fix verification completed!")