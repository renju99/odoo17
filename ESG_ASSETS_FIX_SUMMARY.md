# ESG Module Assets Error Fix

## Problem Description

The ESG reporting module was encountering an error during module upgrade/installation:

```
ValueError: External ID not found in the system: web.assets_backend
```

This error occurred because the module was trying to inherit from a template `web.assets_backend` that doesn't exist in Odoo 17.

## Root Cause

In Odoo 17, the way assets are handled has changed from XML template inheritance to asset bundles defined in the manifest file. The ESG module was using the old approach:

```xml
<template id="assets_backend" inherit_id="web.assets_backend">
    <xpath expr="." position="inside">
        <script type="text/javascript" src="/esg_reporting/static/src/js/esg_advanced_dashboard.js"/>
        <script type="text/javascript" src="/esg_reporting/static/src/js/esg_dashboard.js"/>
    </xpath>
</template>
```

However, `web.assets_backend` is not a template but an asset bundle defined in the web module's manifest.

## Solution

### 1. Removed Problematic File
- Deleted `odoo17/addons/esg_reporting/views/assets.xml`

### 2. Updated Manifest Configuration
Modified `odoo17/addons/esg_reporting/__manifest__.py`:

**Before:**
```python
'data': [
    'security/esg_security.xml',
    'security/ir.model.access.csv',
    'views/assets.xml',  # This was causing the error
    # ... other files
],
```

**After:**
```python
'data': [
    'security/esg_security.xml',
    'security/ir.model.access.csv',
    # Removed 'views/assets.xml'
    # ... other files
],
'assets': {
    'web.assets_backend': [
        'esg_reporting/static/src/js/esg_advanced_dashboard.js',
        'esg_reporting/static/src/js/esg_dashboard.js',
    ],
},
```

## Key Changes

1. **Removed XML template inheritance**: The old approach using `inherit_id="web.assets_backend"` is no longer valid in Odoo 17.

2. **Added assets bundle configuration**: JavaScript files are now added directly to the `web.assets_backend` bundle in the manifest.

3. **Updated file references**: Removed the assets.xml file from the data list and added the assets configuration.

## Verification

The fix has been tested and verified:

- ✅ Odoo can start successfully
- ✅ ESG module directory exists
- ✅ Problematic assets.xml file has been removed
- ✅ Manifest has correct assets configuration

## Files Modified

1. `odoo17/addons/esg_reporting/__manifest__.py` - Updated to use new assets system
2. `odoo17/addons/esg_reporting/views/assets.xml` - Deleted (no longer needed)

## Impact

This fix resolves the module upgrade error and allows the ESG reporting module to load properly in Odoo 17. The JavaScript files will still be loaded correctly, but now through the modern asset bundle system instead of the deprecated XML template inheritance.

## Testing

Run the test script to verify the fix:
```bash
python3 test_esg_fix.py
```

This should output:
```
✅ All tests passed! The fix should resolve the assets error.
```