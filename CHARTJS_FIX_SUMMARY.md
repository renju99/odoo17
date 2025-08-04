# Chart.js Fix Summary

## Problem
The error `ReferenceError: Chart is not defined` was occurring in the ESG Reporting and Facilities Management modules because Chart.js was not properly loaded before being used in the JavaScript code.

## Root Cause
Both modules were trying to use Chart.js in their JavaScript files:
- `esg_reporting/static/src/js/esg_advanced_dashboard.js` - uses `new Chart()` for ESG score charts
- `facilities_management/static/src/js/iot_monitoring.js` - uses `new Chart()` for IoT monitoring charts

However, the modules' manifest files (`__manifest__.py`) were not including the Chart.js library bundle in their assets.

## Solution Applied

### 1. ESG Reporting Module Fix
**File:** `odoo17/addons/esg_reporting/__manifest__.py`

**Before:**
```python
'assets': {
    'web.assets_backend': [
        'esg_reporting/static/src/js/esg_advanced_dashboard.js',
        'esg_reporting/static/src/js/esg_dashboard.js',
        'esg_reporting/static/src/xml/esg_advanced_dashboard.xml',
        'esg_reporting/static/src/xml/esg_dashboard.xml',
    ],
},
```

**After:**
```python
'assets': {
    'web.assets_backend': [
        ('include', 'web.chartjs_lib'),
        'esg_reporting/static/src/js/esg_advanced_dashboard.js',
        'esg_reporting/static/src/js/esg_dashboard.js',
        'esg_reporting/static/src/xml/esg_advanced_dashboard.xml',
        'esg_reporting/static/src/xml/esg_dashboard.xml',
    ],
},
```

### 2. Facilities Management Module Fix
**File:** `odoo17/addons/facilities_management/__manifest__.py`

**Before:**
```python
'assets': {
    'web.assets_backend': [
        'facilities_management/static/src/css/facilities.css',
        'facilities_management/static/src/css/portal.css',
        'facilities_management/static/src/js/dashboard_widgets.js',
        'facilities_management/static/src/js/iot_monitoring.js',
        'facilities_management/static/src/js/mobile_scanner.js',
        'facilities_management/static/src/xml/*.xml',
    ],
},
```

**After:**
```python
'assets': {
    'web.assets_backend': [
        ('include', 'web.chartjs_lib'),
        'facilities_management/static/src/css/facilities.css',
        'facilities_management/static/src/css/portal.css',
        'facilities_management/static/src/js/dashboard_widgets.js',
        'facilities_management/static/src/js/iot_monitoring.js',
        'facilities_management/static/src/js/mobile_scanner.js',
        'facilities_management/static/src/xml/*.xml',
    ],
},
```

## Technical Details

### Chart.js Bundle Location
Chart.js is available in Odoo 17 as a separate bundle called `web.chartjs_lib` which includes:
- `/web/static/lib/Chart/Chart.js` - Main Chart.js library
- `/web/static/lib/chartjs-adapter-luxon/chartjs-adapter-luxon.js` - Luxon adapter for date handling

### How the Fix Works
1. The `('include', 'web.chartjs_lib')` directive tells Odoo to include the Chart.js bundle before loading the module's JavaScript files
2. This ensures that `Chart` is globally available when the module's JavaScript code executes
3. The fix is applied to the `web.assets_backend` bundle since both modules use Chart.js in backend dashboard views

## Verification
The fix has been verified by:
1. ✅ Checking that both manifest files now include the Chart.js bundle
2. ✅ Confirming that the `('include', 'web.chartjs_lib')` directive is present in both modules
3. ✅ Ensuring the syntax is correct and follows Odoo's asset bundle conventions

## Expected Result
After applying this fix and restarting the Odoo server:
- The `ReferenceError: Chart is not defined` error should be resolved
- ESG dashboard charts should render properly
- IoT monitoring charts in Facilities Management should work correctly
- All Chart.js functionality should be available in both modules

## Next Steps
1. Restart the Odoo server to apply the changes
2. Clear the browser cache to ensure new assets are loaded
3. Test the ESG dashboard and IoT monitoring features
4. Verify that all charts are rendering correctly

## Related Modules
Other modules that use Chart.js and already have the correct setup:
- `survey` module - includes Chart.js in `survey.survey_assets` bundle
- `website_links` module - uses Chart.js in frontend assets (already available)
- `spreadsheet` module - includes Chart.js in its assets

## Files Modified
1. `odoo17/addons/esg_reporting/__manifest__.py`
2. `odoo17/addons/facilities_management/__manifest__.py`

## Error Resolution
The original error:
```
UncaughtPromiseError > ReferenceError
Uncaught Promise > Chart is not defined
ReferenceError: Chart is not defined
    createESGScoreChart@http://localhost:8069/web/assets/7965c43/web.assets_web.min.js:18189:143
```

Should now be resolved as Chart.js will be properly loaded before the ESG dashboard JavaScript code executes.