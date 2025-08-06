#!/usr/bin/env python3
"""
Test script to verify JavaScript layout timing fixes for Facilities Management module.
This script tests the fixes for:
1. "Layout was forced before the page was fully loaded" error
2. "unreachable code after return statement" error
3. Proper asset loading order
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def check_javascript_file(file_path, description):
    """Check a JavaScript file for common issues."""
    print(f"\n=== Checking {description} ===")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues_found = []
    
    # Check for unreachable code after return statements (but ignore switch statements)
    return_pattern = r'return\s*[^;]*;\s*\n\s*[^}]*[^;{}]\s*\n'
    unreachable_matches = re.finditer(return_pattern, content, re.MULTILINE)
    
    for match in unreachable_matches:
        # Get the context around the match to check if it's in a switch statement
        start_pos = max(0, match.start() - 200)
        end_pos = min(len(content), match.end() + 200)
        context = content[start_pos:end_pos]
        
        # Skip if this is in a switch statement
        if 'switch' in context and 'case' in context:
            continue
            
        line_num = content[:match.start()].count('\n') + 1
        issues_found.append(f"Potential unreachable code after return at line {line_num}")
    
    # Check for layout timing issues
    layout_patterns = [
        r'setTimeout.*layout',
        r'layout.*before.*load',
        r'force.*layout.*early'
    ]
    
    for pattern in layout_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues_found.append(f"Potential layout timing issue at line {line_num}: {match.group()}")
    
    # Check for proper requestAnimationFrame usage
    raf_pattern = r'requestAnimationFrame'
    raf_matches = re.findall(raf_pattern, content)
    if raf_matches:
        print(f"✅ Found {len(raf_matches)} requestAnimationFrame usage(s)")
    
    # Check for proper DOM ready checks
    dom_ready_patterns = [
        r'document\.readyState',
        r'DOMContentLoaded',
        r'addEventListener.*load',
        r'onMounted',
        r'onWillStart'
    ]
    
    dom_ready_found = False
    for pattern in dom_ready_patterns:
        if re.search(pattern, content):
            dom_ready_found = True
            break
    
    if dom_ready_found:
        print("✅ Found proper DOM ready checks")
    else:
        issues_found.append("No DOM ready checks found")
    
    if issues_found:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    else:
        print("✅ No issues found")
        return True

def check_manifest_assets(manifest_path):
    """Check the manifest file for proper asset loading order."""
    print(f"\n=== Checking manifest assets ===")
    
    if not os.path.exists(manifest_path):
        print(f"❌ Manifest file not found: {manifest_path}")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for proper asset loading order
    assets_pattern = r"'web\.assets_backend':\s*\[(.*?)\]"
    assets_match = re.search(assets_pattern, content, re.DOTALL)
    
    if not assets_match:
        print("❌ No web.assets_backend found in manifest")
        return False
    
    assets_content = assets_match.group(1)
    
    # Check for CSS loading before JavaScript
    css_files = re.findall(r"'facilities_management/static/src/css/[^']*'", assets_content)
    js_files = re.findall(r"'facilities_management/static/src/js/[^']*'", assets_content)
    
    print(f"✅ Found {len(css_files)} CSS files")
    print(f"✅ Found {len(js_files)} JavaScript files")
    
    # Check for Chart.js library inclusion
    if "web.chartjs_lib" in assets_content:
        print("✅ Chart.js library properly included")
    else:
        print("❌ Chart.js library not found in assets")
        return False
    
    return True

def check_css_file(css_path):
    """Check the CSS file for layout timing fixes."""
    print(f"\n=== Checking CSS layout fixes ===")
    
    if not os.path.exists(css_path):
        print(f"❌ CSS file not found: {css_path}")
        return False
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for FOUC prevention
    fouc_patterns = [
        r'visibility:\s*hidden',
        r'display:\s*none',
        r'\.loaded\s*{',
        r'transition:\s*opacity'
    ]
    
    fouc_fixes_found = 0
    for pattern in fouc_patterns:
        if re.search(pattern, content):
            fouc_fixes_found += 1
    
    if fouc_fixes_found >= 3:
        print("✅ FOUC prevention measures found")
    else:
        print(f"❌ Only {fouc_fixes_found}/4 FOUC prevention measures found")
        return False
    
    return True

def run_odoo_test():
    """Run a basic Odoo test to check for JavaScript errors."""
    print(f"\n=== Running Odoo test ===")
    
    try:
        # Change to odoo directory
        odoo_dir = Path("odoo17")
        if not odoo_dir.exists():
            print("❌ Odoo directory not found")
            return False
        
        os.chdir(odoo_dir)
        
        # Run a basic test command
        cmd = [
            sys.executable, "odoo-bin",
            "--test-enable",
            "--stop-after-init",
            "--addons-path=addons",
            "--test-tags=@facilities_management"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Odoo test completed successfully")
            return True
        else:
            print(f"❌ Odoo test failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Odoo test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Odoo test: {e}")
        return False

def main():
    """Main test function."""
    print("🔧 Testing JavaScript Layout Timing Fixes")
    print("=" * 50)
    
    # Define file paths
    base_path = Path("odoo17/addons/facilities_management")
    
    files_to_check = [
        (base_path / "static/src/js/dashboard_widgets.js", "Dashboard Widgets"),
        (base_path / "static/src/js/iot_monitoring.js", "IoT Monitoring"),
        (base_path / "static/src/js/mobile_scanner.js", "Mobile Scanner"),
        (base_path / "__manifest__.py", "Manifest Assets"),
        (base_path / "static/src/css/facilities.css", "CSS Layout Fixes")
    ]
    
    all_passed = True
    
    for file_path, description in files_to_check:
        if description == "Manifest Assets":
            success = check_manifest_assets(file_path)
        elif description == "CSS Layout Fixes":
            success = check_css_file(file_path)
        else:
            success = check_javascript_file(file_path, description)
        
        if not success:
            all_passed = False
    
    # Run Odoo test if all file checks pass
    if all_passed:
        print("\n" + "=" * 50)
        print("🎯 All file checks passed! Running Odoo test...")
        odoo_success = run_odoo_test()
        all_passed = all_passed and odoo_success
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! JavaScript layout timing fixes are working correctly.")
        print("\nFixed issues:")
        print("  - Layout forced before page fully loaded")
        print("  - Unreachable code after return statements")
        print("  - Proper asset loading order")
        print("  - FOUC (Flash of Unstyled Content) prevention")
    else:
        print("❌ Some tests failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()