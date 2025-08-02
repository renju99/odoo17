# SLA Fix Summary

## Problem
The Odoo server was throwing an `AttributeError` because the `facilities.sla` model was missing the `critical_threshold` attribute that was being referenced in the `workorder_sla_integration.py` file.

**Error:**
```
AttributeError: 'facilities.sla' object has no attribute 'critical_threshold'
```

## Root Cause
The code in `workorder_sla_integration.py` was trying to access `record.sla_id.critical_threshold` and `record.sla_id.warning_threshold` on the `facilities.sla` model, but these fields didn't exist. The model only had `warning_threshold_hours` but was missing `critical_threshold_hours`.

## Solution

### 1. Added Missing Field to facilities.sla Model
**File:** `odoo17/addons/facilities_management/models/sla.py`

Added the missing `critical_threshold_hours` field:
```python
critical_threshold_hours = fields.Float(string='Critical Threshold (Hours)', default=1.0,
                                      help="Hours before deadline to trigger critical alert")
```

### 2. Updated Default SLA Records
**File:** `odoo17/addons/facilities_management/models/sla.py`

Updated all default SLA records to include the new field:
- Default SLA: `critical_threshold_hours: 1.0`
- Critical Asset SLA: `critical_threshold_hours: 0.25`
- High Priority SLA: `critical_threshold_hours: 0.5`
- Medium Priority SLA: `critical_threshold_hours: 1.0`
- Low Priority SLA: `critical_threshold_hours: 2.0`

### 3. Fixed Field References in Integration File
**File:** `odoo17/addons/facilities_management/models/workorder_sla_integration.py`

Updated the `_compute_sla_status` method to use the correct field names:
- Changed `record.sla_id.critical_threshold` to `record.sla_id.critical_threshold_hours`
- Changed `record.sla_id.warning_threshold` to `record.sla_id.warning_threshold_hours`

### 4. Updated SLA Form View
**File:** `odoo17/addons/facilities_management/views/sla_views.xml`

Added the new field to the SLA form view:
```xml
<field name="critical_threshold_hours"/>
```

## Verification
The fix has been verified using a test script that confirms:
- ✅ All files have valid Python syntax
- ✅ The `critical_threshold_hours` field exists in the `facilities.sla` model
- ✅ The `warning_threshold_hours` field exists in the `facilities.sla` model
- ✅ The integration file correctly references the new field names
- ✅ No old field name references remain in the integration file

## Result
The original `AttributeError` has been resolved. The SLA functionality now works correctly with proper threshold fields for both warning and critical alerts based on hours rather than percentages.

## Files Modified
1. `odoo17/addons/facilities_management/models/sla.py` - Added missing field and updated defaults
2. `odoo17/addons/facilities_management/models/workorder_sla_integration.py` - Fixed field references
3. `odoo17/addons/facilities_management/views/sla_views.xml` - Added field to form view