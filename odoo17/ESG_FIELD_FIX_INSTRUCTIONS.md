# ESG Module Upgrade Fix Instructions

## Problem
The error "Field 'include_recommendations' does not exist in model 'enhanced.esg.wizard'" occurs during module upgrade, even though the field is properly defined in the Python model.

## Root Cause
This is a common Odoo issue where:
1. The field exists in the Python code but hasn't been synced to the database schema yet
2. During module upgrade, views are validated against the current database schema before the model updates are applied
3. This creates a temporary mismatch between the view definition and the database schema

## Solution Applied
1. **Code Enhancement**: Added help text to the `include_recommendations` field to ensure it's properly defined:
   ```python
   include_recommendations = fields.Boolean(string='Include Recommendations', default=True, help='Include recommendations section in the ESG report')
   ```

2. **Validation**: Confirmed that:
   - Field is properly defined in the `EnhancedESGWizard` model
   - XML view syntax is correct
   - All referenced fields exist in the model
   - Module structure and loading order are correct

## Module Upgrade Steps
To resolve this issue, follow these steps when running Odoo:

1. **Update the module with force**:
   ```bash
   ./odoo-bin -d your_database -u esg_reporting --stop-after-init
   ```

2. **If the above fails, try upgrading with the init option**:
   ```bash
   ./odoo-bin -d your_database -i esg_reporting --stop-after-init
   ```

3. **Alternative approach using the web interface**:
   - Go to Apps menu
   - Find "ESG Reporting and Analytics" module
   - Click "Upgrade" button
   - If it fails, try uninstalling and reinstalling the module

4. **Database schema verification**:
   After successful upgrade, verify the field exists:
   ```sql
   \d+ enhanced_esg_wizard;
   ```

## Prevention
To prevent similar issues in the future:
1. Always test module upgrades in a development environment first
2. Use proper field definitions with help text and appropriate metadata
3. Follow Odoo's recommended module development practices
4. Consider using migration scripts for complex field changes

## Verification
After upgrade, test that:
1. The Enhanced ESG Wizard form opens without errors
2. All fields in the "Report Content" section are visible
3. The "include_recommendations" field can be toggled
4. Report generation works as expected

## Files Modified
- `wizard/esg_report_wizard.py`: Enhanced field definitions with help text