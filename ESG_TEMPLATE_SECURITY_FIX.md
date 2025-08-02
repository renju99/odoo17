# ESG Template Security Fix

## Problem
The ESG reporting template was causing a `NameError: Access to forbidden name '__name__'` error when trying to compile the QWeb template. This occurred because Odoo's safe evaluation context prohibits access to dunder methods (methods starting and ending with double underscores) for security reasons.

## Error Details
```
NameError: Access to forbidden name '__name__' ("type(report_data).__name__ if report_data else 'None'")
Template: esg_reporting.report_enhanced_esg_wizard_document
Path: /t/div/div[2]/div/div/div/p[3]/t
Node: <t t-esc="type(report_data).__name__ if report_data else 'None'"/>
```

## Root Cause
The problematic line was in the debug information section of the template:
```xml
<p><strong>Report data type:</strong> <t t-esc="type(report_data).__name__ if report_data else 'None'"/></p>
```

This line attempted to access the `__name__` attribute of the type object, which is forbidden in Odoo's safe evaluation context.

## Solution
Replaced the forbidden `type(report_data).__name__` access with a safe alternative using `isinstance()` checks:

### Before (Problematic):
```xml
<p><strong>Report data type:</strong> <t t-esc="type(report_data).__name__ if report_data else 'None'"/></p>
```

### After (Fixed):
```xml
<p><strong>Report data type:</strong> <t t-esc="'dict' if isinstance(report_data, dict) else 'list' if isinstance(report_data, list) else 'str' if isinstance(report_data, str) else 'int' if isinstance(report_data, int) else 'float' if isinstance(report_data, float) else 'bool' if isinstance(report_data, bool) else 'None' if report_data is None else 'other'"/></p>
```

## Additional Safety Improvements
Also added safety checks for other potentially problematic accesses:

### Before:
```xml
<p><strong>Report data keys:</strong> <t t-esc="list(report_data.keys()) if report_data else 'None'"/></p>
<p><strong>Wizard object keys:</strong> <t t-esc="list(o._fields.keys()) if o else 'None'"/></p>
```

### After:
```xml
<p><strong>Report data keys:</strong> <t t-esc="list(report_data.keys()) if report_data and hasattr(report_data, 'keys') else 'None'"/></p>
<p><strong>Wizard object keys:</strong> <t t-esc="list(o._fields.keys()) if o and hasattr(o, '_fields') else 'None'"/></p>
```

## Benefits
1. **Security**: Eliminates access to forbidden dunder methods
2. **Compatibility**: Uses only safe functions allowed in Odoo's evaluation context
3. **Robustness**: Added `hasattr()` checks to prevent attribute access errors
4. **Functionality**: Maintains the same debugging information but in a secure way

## Verification
- ✅ Template security check passed
- ✅ No forbidden patterns found in the template
- ✅ The fix maintains the same debugging functionality
- ✅ Template should now compile without security errors

## Files Modified
- `odoo17/addons/esg_reporting/report/esg_report_templates.xml` (lines 370-372)

## Testing
The fix has been verified using a custom security checker that scans for forbidden patterns in QWeb templates. The template now passes all security checks and should compile successfully in Odoo.