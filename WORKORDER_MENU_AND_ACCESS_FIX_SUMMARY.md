# Work Order Menu and Access Rights Fix Summary

## Issues Identified

1. **Duplicate Work Order Menus**: Two work order menu items were appearing:
   - "Work Orders" 
   - "Work Orders (Enhanced)"

2. **Missing Access Rights**: Several models were missing access rights, causing access denied errors:
   - `maintenance.escalation.log`
   - `facilities.asset.sensor`
   - `facilities.asset.sensor.data`
   - `facilities.asset.threshold`
   - `facilities.asset.scan.wizard`
   - `facilities.import.wizard`

## Changes Made

### 1. Menu Consolidation (`facility_asset_menus.xml`)

**Removed:**
- `menu_maintenance_workorders_enhanced` menu item
- `action_maintenance_workorder_enhanced` action

**Updated:**
- Modified `action_maintenance_workorder` to use enhanced views by default:
  - Changed tree view from `view_maintenance_workorder_tree` to `view_maintenance_workorder_enhanced_tree`
  - Changed form view from `view_workorder_form` to `view_maintenance_workorder_enhanced_form`
  - Added enhanced search view reference
  - Updated help text to mention SLA tracking and enhanced features

### 2. Access Rights Fix (`ir.model.access.csv`)

**Added missing access rights for:**
```
access_maintenance_escalation_log_user,maintenance.escalation.log.user,model_maintenance_escalation_log,base.group_user,1,1,1,1
access_facilities_asset_sensor_user,facilities.asset.sensor.user,model_facilities_asset_sensor,base.group_user,1,1,1,1
access_facilities_asset_sensor_data_user,facilities.asset.sensor.data.user,model_facilities_asset_sensor_data,base.group_user,1,1,1,1
access_facilities_asset_threshold_user,facilities.asset.threshold.user,model_facilities_asset_threshold,base.group_user,1,1,1,1
access_facilities_asset_scan_wizard_user,facilities.asset.scan.wizard.user,model_facilities_asset_scan_wizard,base.group_user,1,1,1,1
access_facilities_import_wizard_user,facilities.import.wizard.user,model_facilities_import_wizard,base.group_user,1,1,1,1
```

## Result

1. **Single Work Order Menu**: Now only one "Work Orders" menu item appears with enhanced functionality by default
2. **No Access Rights Errors**: All models now have proper access rights defined
3. **Enhanced Features Available**: Users get SLA tracking and enhanced features without needing a separate menu

## Files Modified

1. `odoo17/addons/facilities_management/views/facility_asset_menus.xml`
2. `odoo17/addons/facilities_management/security/ir.model.access.csv`

## Next Steps

After making these changes, you should:

1. Restart the Odoo server
2. Update the facilities_management module
3. Test that:
   - Only one "Work Orders" menu appears
   - No access rights errors in the logs
   - Enhanced work order features are available in the single menu

The enhanced functionality (SLA tracking, etc.) is now integrated into the main work order interface, providing a cleaner user experience while maintaining all the advanced features.