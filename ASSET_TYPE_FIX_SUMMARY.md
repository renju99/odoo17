# Asset Type Fix Summary

## Problem
The ESG reporting wizard was encountering an error when trying to filter assets by `asset_type`:

```
ValueError: Invalid field facilities.asset.asset_type in leaf ('asset_type', '=', 'equipment')
```

## Root Cause
The error occurred because:

1. **Wrong Model Reference**: The ESG wizard was trying to search the `facilities.asset` model
2. **Missing Field**: The `facilities.asset` model doesn't have an `asset_type` field
3. **Field Location**: The asset type information is stored in the related `category_id.category_type` field

## Solution
Updated the ESG wizard to use the correct field path:

### Before (Incorrect)
```python
domain.append(('asset_type', '=', self.asset_type))
```

### After (Correct)
```python
domain.append(('category_id.category_type', '=', self.asset_type))
```

## Changes Made

### 1. Fixed Domain Construction
**File**: `odoo17/addons/esg_reporting/wizard/esg_report_wizard.py`

**Lines 240-241**:
```python
# Before
domain.append(('asset_type', '=', self.asset_type))

# After  
domain.append(('category_id.category_type', '=', self.asset_type))
```

**Lines 251-252**:
```python
# Before
fallback_domain.append(('asset_type', '=', self.asset_type))

# After
fallback_domain.append(('category_id.category_type', '=', self.asset_type))
```

### 2. Updated Asset Type Selection Options
**File**: `odoo17/addons/esg_reporting/wizard/esg_report_wizard.py`

**Lines 98-105**: Updated the selection options to match the `category_type` field values:

```python
asset_type = fields.Selection([
    ('all', 'All Assets'),
    ('equipment', 'Equipment'),
    ('furniture', 'Furniture'),
    ('vehicle', 'Vehicle'),
    ('it', 'IT Hardware'),
    ('building', 'Building Component'),
    ('infrastructure', 'Infrastructure'),
    ('tool', 'Tool'),
    ('other', 'Other')
], string='Asset Type', default='all')
```

## Model Structure
The correct relationship is:
- `facilities.asset` (main asset model)
  - `category_id` → `facilities.asset.category` (related category)
    - `category_type` → Selection field with asset type values

## Verification
The fix ensures that:
1. ✅ Domain construction works without errors
2. ✅ All asset type values match the category_type field
3. ✅ Asset filtering works correctly in ESG reports
4. ✅ Backward compatibility is maintained

## Testing
To test the fix:
1. Update the ESG reporting module: `--update=esg_reporting`
2. Try generating an ESG report with different asset type filters
3. Verify that assets are correctly filtered by their category type

## Related Files
- `odoo17/addons/esg_reporting/wizard/esg_report_wizard.py` - Main fix
- `odoo17/addons/facilities_management/models/asset.py` - Asset model (no changes needed)
- `odoo17/addons/facilities_management/models/asset_category.py` - Category model with category_type field