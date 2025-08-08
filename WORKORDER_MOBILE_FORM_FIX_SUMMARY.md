# Workorder Mobile Form Fix Summary

## Issue
The Odoo server was throwing a `ParseError` when trying to upgrade the facilities_management module. The error indicated that the field `workorder_status` was being used in modifiers but was not present in the view.

## Error Details
```
Error while validating view near:
<form string="Work Order (Mobile)" class="o_mobile_form" __validate__="1">
    <header>
        <field name="status" invisible="1"/>

Field 'workorder_status' used in modifier 'invisible' (workorder_status != 'in_progress') must be present in view but is missing.
```

## Root Cause
In the file `odoo17/addons/facilities_management/views/maintenance_workorder_mobile_form.xml`, the view was referencing `workorder_status` in modifiers on lines 174 and 177, but this field doesn't exist in the `maintenance.workorder` model.

The `workorder_status` field exists in the `maintenance.workorder.task` model (as a related field to `workorder_id.state`), but not in the main workorder model itself.

## Solution
Replaced `workorder_status` with `status` in the modifiers, since `status` is a related field to `state` in the `maintenance.workorder` model.

### Changes Made
- **File**: `odoo17/addons/facilities_management/views/maintenance_workorder_mobile_form.xml`
- **Lines**: 174 and 177
- **Change**: Replaced `workorder_status` with `status` in the `readonly` and `invisible` modifiers

### Before:
```xml
<field name="is_done" widget="boolean_toggle" readonly="workorder_status != 'in_progress'"/>
<button name="toggle_task_completion" type="object" string="Toggle" class="btn btn-secondary btn-sm" invisible="workorder_status != 'in_progress'"/>
```

### After:
```xml
<field name="is_done" widget="boolean_toggle" readonly="status != 'in_progress'"/>
<button name="toggle_task_completion" type="object" string="Toggle" class="btn btn-secondary btn-sm" invisible="status != 'in_progress'"/>
```

## Verification
- ✅ All references to `workorder_status` have been removed from the mobile form view
- ✅ The `status` field exists in the `maintenance.workorder` model (line 182)
- ✅ The `status` field is related to `state` which has the correct selection values
- ✅ No other similar issues found in the codebase

## Impact
This fix resolves the module upgrade error and allows the facilities_management module to be properly installed/upgraded. The mobile workorder form will now function correctly with proper field references.