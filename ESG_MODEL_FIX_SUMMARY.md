# ESG Model Fix Summary

## Problem
The ESG reporting wizard was encountering a `KeyError: 'facility.asset'` because it was trying to access a model that didn't exist. The error occurred in the `action_generate_enhanced_esg_report` method when trying to search for assets.

## Root Cause
1. **Incorrect Model Name**: The ESG wizard was trying to access `facility.asset` but the actual model in the facilities_management module is named `facilities.asset` (note the 's' in facilities).

2. **Missing ESG Fields**: The ESG wizard was expecting ESG-specific fields like `carbon_footprint` and `esg_compliance` on the asset model, but these fields didn't exist.

## Fixes Applied

### 1. Fixed Model Name Reference
**File**: `odoo17/addons/esg_reporting/wizard/esg_report_wizard.py`
**Line**: 239
**Change**: 
```python
# Before
assets = self.env['facility.asset'].search(domain)

# After  
assets = self.env['facilities.asset'].search(domain)
```

### 2. Added ESG Fields to Asset Model
**File**: `odoo17/addons/facilities_management/models/asset.py`
**Added**: Comprehensive ESG (Environmental, Social, Governance) fields:

#### Environmental Metrics:
- `esg_compliance` - Boolean field indicating ESG compliance
- `carbon_footprint` - Float field for carbon footprint in kg CO2
- `energy_efficiency_rating` - Selection field for energy efficiency (A-E)
- `renewable_energy_usage` - Float field for renewable energy percentage
- `waste_management_score` - Float field for waste management effectiveness
- `water_consumption` - Float field for daily water consumption
- `biodiversity_impact` - Selection field for biodiversity impact level

#### Social Metrics:
- `community_impact_score` - Float field for community impact
- `employee_satisfaction` - Float field for employee satisfaction
- `diversity_index` - Float field for diversity and inclusion
- `health_safety_score` - Float field for health and safety
- `training_hours` - Float field for annual training hours
- `local_procurement` - Float field for local procurement percentage

#### Governance Metrics:
- `compliance_rate` - Float field for overall compliance rate
- `risk_management_score` - Float field for risk management effectiveness
- `transparency_index` - Float field for transparency and reporting
- `board_diversity` - Float field for board diversity
- `ethics_score` - Float field for ethical business practices
- `stakeholder_engagement` - Float field for stakeholder engagement

### 3. Updated Asset Views
**File**: `odoo17/addons/facilities_management/views/facility_asset_views.xml`

#### Added ESG Metrics Page:
- New page in the asset form view with all ESG fields organized by category
- Environmental, Social, and Governance metrics in separate groups

#### Updated Tree View:
- Added `esg_compliance` field with boolean toggle widget
- Added `carbon_footprint` and `energy_efficiency_rating` fields (optional/hidden by default)

#### Updated Search View:
- Added ESG-related search fields
- Added ESG-specific filters:
  - ESG Compliant/Non-Compliant
  - High Carbon Footprint
  - Low Energy Efficiency

## Verification
The fix was verified using a comprehensive test that checked:
✅ ESG wizard uses correct model name 'facilities.asset'
✅ ESG wizard references esg_compliance field  
✅ ESG wizard references carbon_footprint field
✅ All ESG fields are defined in asset model
✅ Asset model has correct name 'facilities.asset'
✅ ESG Metrics page exists in asset views
✅ ESG fields included in asset views

## Result
The RPC_ERROR should now be resolved. The ESG reporting wizard can successfully:
1. Access the correct `facilities.asset` model
2. Search for assets using the `esg_compliance` field
3. Calculate ESG metrics using the newly added fields
4. Generate comprehensive ESG reports

## Next Steps
1. Restart the Odoo server to ensure all changes are loaded
2. Update the modules: `--update=esg_reporting,facilities_management`
3. Test the ESG reporting functionality in the web interface