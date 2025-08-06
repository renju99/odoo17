#!/usr/bin/env python3
"""
Test script to verify that the facilities_management module can be installed
without the menu reference error.
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_module_installation():
    """Test if the module can be installed without errors."""
    
    print("Testing facilities_management module installation...")
    
    # Check if we're in the right directory
    if not os.path.exists("odoo17/odoo-bin"):
        print("Error: odoo-bin not found. Please run this script from the workspace root.")
        return False
    
    # Try to find Python executable
    python_cmd = None
    possible_paths = [
        "/home/ranjith/odoo17env/bin/python",
        "python3",
        "python",
        sys.executable
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                python_cmd = path
                print(f"Using Python: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if not python_cmd:
        print("Error: Could not find a working Python executable")
        return False
    
    # Test the module installation
    try:
        cmd = [
            python_cmd, "odoo17/odoo-bin",
            "-d", "odoo17",
            "-u", "facilities_management",
            "--stop-after-init",
            "--log-level=error"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=60,
                              cwd=".")
        
        if result.returncode == 0:
            print("✅ SUCCESS: Module installed without errors!")
            return True
        else:
            print("❌ ERROR: Module installation failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Installation timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_menu_references():
    """Check for any remaining problematic menu references."""
    
    print("\nChecking for problematic menu references...")
    
    # Check for the specific error we fixed
    sla_file = "odoo17/addons/facilities_management/views/sla_views.xml"
    
    if os.path.exists(sla_file):
        with open(sla_file, 'r') as f:
            content = f.read()
            
        if 'menu_facilities_maintenance' in content:
            print("❌ ERROR: Found reference to non-existent menu_facilities_maintenance")
            return False
        else:
            print("✅ SUCCESS: No references to menu_facilities_maintenance found")
            return True
    else:
        print("❌ ERROR: SLA views file not found")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("FACILITIES MANAGEMENT MODULE FIX TEST")
    print("=" * 60)
    
    # Check menu references first
    menu_ok = check_menu_references()
    
    if not menu_ok:
        print("\n❌ Menu reference check failed. Please fix the issues first.")
        return False
    
    # Test module installation
    install_ok = test_module_installation()
    
    if install_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("The facilities_management module should now install without the menu reference error.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return install_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)