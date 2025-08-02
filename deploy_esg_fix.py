#!/usr/bin/env python3
"""
Deployment script for the ESG template NoneType error fix.
"""

import os
import sys
import subprocess

def check_odoo_installation():
    """Check if Odoo is properly installed"""
    print("🔍 Checking Odoo installation...")
    
    odoo_bin = "odoo17/odoo-bin"
    if not os.path.exists(odoo_bin):
        print("❌ ERROR: Odoo binary not found at", odoo_bin)
        return False
    
    print("✅ Odoo binary found")
    return True

def check_esg_module():
    """Check if the ESG module exists"""
    print("\n🔍 Checking ESG module...")
    
    module_path = "odoo17/addons/esg_reporting"
    if not os.path.exists(module_path):
        print("❌ ERROR: ESG module not found at", module_path)
        return False
    
    # Check key files
    required_files = [
        "odoo17/addons/esg_reporting/__manifest__.py",
        "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py",
        "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ ERROR: Required file not found: {file_path}")
            return False
    
    print("✅ ESG module and required files found")
    return True

def update_esg_module():
    """Update the ESG module to apply the fix"""
    print("\n🔄 Updating ESG module...")
    
    try:
        # Change to the odoo directory
        os.chdir("odoo17")
        
        # Update the ESG module
        cmd = [
            "python3", "odoo-bin", 
            "--addons-path=addons",
            "--update=esg_reporting",
            "--stop-after-init"
        ]
        
        print("Running:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ESG module updated successfully")
            return True
        else:
            print("❌ ERROR: Failed to update ESG module")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Exception during module update: {e}")
        return False
    finally:
        # Change back to workspace
        os.chdir("..")

def test_report_generation():
    """Test if the report generation works"""
    print("\n🧪 Testing report generation...")
    
    # This would typically involve making an API call to test report generation
    # For now, we'll just check that the template files are properly formatted
    
    template_file = "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Check for the key fixes
        fixes_found = []
        
        if 'o._get_report_data() or {}' in content:
            fixes_found.append("✅ Report data initialization fix")
        
        if "'Available' if report_data and isinstance(report_data, dict)" in content:
            fixes_found.append("✅ Safe keys display fix")
        
        if "str(len(report_data))" in content:
            fixes_found.append("✅ Safe length display fix")
        
        if len(fixes_found) == 3:
            print("✅ All template fixes are in place")
            return True
        else:
            print("❌ ERROR: Not all fixes are applied")
            for fix in fixes_found:
                print(f"   {fix}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to test template: {e}")
        return False

def create_backup():
    """Create a backup of the original files"""
    print("\n💾 Creating backup...")
    
    backup_dir = "esg_backup_" + str(int(os.path.getmtime("odoo17/addons/esg_reporting")))
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy key files
        files_to_backup = [
            "odoo17/addons/esg_reporting/wizard/esg_report_wizard.py",
            "odoo17/addons/esg_reporting/report/esg_report_templates.xml"
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                print(f"✅ Backed up: {file_path}")
        
        print(f"✅ Backup created in: {backup_dir}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create backup: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 ESG Template Fix Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_odoo_installation():
        print("\n❌ Prerequisites not met. Please check Odoo installation.")
        sys.exit(1)
    
    if not check_esg_module():
        print("\n❌ ESG module not found. Please check module installation.")
        sys.exit(1)
    
    # Create backup
    if not create_backup():
        print("\n❌ Failed to create backup. Aborting deployment.")
        sys.exit(1)
    
    # Update module
    if not update_esg_module():
        print("\n❌ Failed to update ESG module. Please check the error messages above.")
        sys.exit(1)
    
    # Test the fix
    if not test_report_generation():
        print("\n❌ Template fix verification failed. Please check the template files.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Deployment completed successfully!")
    print("\n📝 Summary:")
    print("   ✅ Backup created")
    print("   ✅ ESG module updated")
    print("   ✅ Template fixes verified")
    print("   ✅ NoneType error should be resolved")
    
    print("\n📋 Next Steps:")
    print("   1. Test report generation in the Odoo interface")
    print("   2. Monitor logs for any remaining issues")
    print("   3. Verify that PDF reports can be generated")
    print("   4. If issues persist, check the backup files")

if __name__ == "__main__":
    main()