# ESG Report Generation Guide

## Overview

The Facilities Management Module now includes comprehensive ESG (Environmental, Social, and Governance) reporting functionality. This feature allows you to track and report on ESG compliance metrics for your facility assets.

## Features Added

### 1. ESG Compliance Tracking
- **Environmental Impact**: Track low, medium, or high environmental impact
- **Energy Efficiency Rating**: A-E rating system for energy efficiency
- **Carbon Footprint**: Track CO2 emissions in kg/year
- **Renewable Energy**: Flag assets using renewable energy sources
- **Safety Compliance**: Track safety compliance status
- **Accessibility Compliance**: Track accessibility compliance
- **Social Impact Score**: 1-10 rating for social impact
- **Regulatory Compliance**: Track regulatory compliance status
- **Certifications**: Link multiple certifications to assets
- **Audit Tracking**: Track audit dates and upcoming audits

### 2. Asset Certification Management
- Create and manage asset certifications
- Track certification types (Environmental, Social, Governance, Safety, Quality)
- Monitor certification expiry dates
- Link certifications to assets

### 3. ESG Report Generation
- Generate comprehensive ESG reports
- Filter by date range, asset type, and compliance status
- Include environmental, social, and governance metrics
- Generate PDF reports with charts and recommendations

## Installation

1. **Install the Module**: Install the `facilities_management_module` in your Odoo instance
2. **Load Demo Data**: The module includes demo data with sample assets and certifications
3. **Configure Assets**: Add ESG compliance data to your existing assets

## How to Use

### 1. Adding ESG Data to Assets

1. Navigate to **Assets** in the Facilities Management menu
2. Open an asset record
3. Scroll to the **ESG Compliance** section
4. Fill in the relevant ESG fields:
   - **Environmental**: Impact level, energy rating, carbon footprint, renewable energy
   - **Social**: Safety compliance, accessibility, social impact score
   - **Governance**: Regulatory compliance, certifications, audit dates

### 2. Managing Certifications

1. Navigate to **Assets > Certifications**
2. Create new certifications with:
   - Name and code
   - Certification type (Environmental, Social, Governance, Safety, Quality)
   - Issuing body
   - Issue and expiry dates
   - Description and requirements

### 3. Generating ESG Reports

1. Navigate to **Assets > ESG Reports > Generate ESG Report**
2. Configure report parameters:
   - **Report Type**: Environmental, Social, Governance, or Comprehensive
   - **Date Range**: Select the period for analysis
   - **Asset Type**: Filter by specific asset types
   - **Include ESG Compliance Assets Only**: Filter for assets requiring ESG compliance
   - **Include Charts and Graphs**: Add visual elements to the report
   - **Include Recommendations**: Add improvement suggestions

3. Click **Generate ESG Report** to create a PDF report

## Report Contents

### Environmental Metrics
- Total carbon footprint across all assets
- Number of renewable energy assets
- Energy efficiency distribution
- Environmental impact distribution

### Social Metrics
- Number of safety compliant assets
- Number of accessibility compliant assets
- Average social impact score
- Social impact trends

### Governance Metrics
- Number of regulatory compliant assets
- Assets with certifications
- Total certifications count
- Upcoming audits (within 30 days)

### Asset Details
- Complete list of assets with ESG data
- Environmental impact levels
- Energy efficiency ratings
- Compliance status

### Recommendations
- Suggestions for improving energy efficiency
- Renewable energy implementation advice
- Accessibility compliance improvements
- Audit scheduling recommendations
- Certification acquisition guidance

## Demo Data

The module includes demo data with:
- 3 sample certifications (ISO 14001, OHSAS 18001, ISO 9001)
- 4 sample assets with ESG data:
  - HVAC System (high environmental impact)
  - Solar Panel System (renewable energy, low impact)
  - Elevator System (medium impact)
  - LED Lighting System (low impact, high efficiency)

## Troubleshooting

### Common Issues

1. **Report Not Generating**
   - Ensure you have assets with ESG data
   - Check that the date range includes assets
   - Verify asset types are correctly set

2. **Missing ESG Fields**
   - Make sure the module is properly installed
   - Check that the asset form view includes ESG sections
   - Restart Odoo if fields don't appear

3. **PDF Generation Errors**
   - Ensure wkhtmltopdf is installed on your server
   - Check server logs for PDF generation errors
   - Verify report template files are present

### Support

If you encounter issues:
1. Check the Odoo server logs for error messages
2. Verify all module files are properly installed
3. Ensure demo data is loaded for testing
4. Contact your system administrator for server configuration issues

## Future Enhancements

Potential future improvements:
- ESG dashboard with charts and graphs
- Automated ESG compliance scoring
- Integration with external ESG reporting standards
- Email scheduling for ESG reports
- ESG trend analysis over time
- Integration with sustainability reporting frameworks

## Technical Details

### Models Added
- `facility.asset` (enhanced with ESG fields)
- `asset.certification` (new model)
- `esg.report.wizard` (new wizard)

### Views Added
- ESG compliance section in asset forms
- Asset certification management views
- ESG report wizard interface
- ESG report menus

### Reports Added
- ESG report PDF template
- Comprehensive ESG metrics calculation
- Professional report formatting

This ESG reporting functionality provides a comprehensive solution for tracking and reporting on environmental, social, and governance compliance in your facility management operations.