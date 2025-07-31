# ESG Reporting Module for Odoo 19

A comprehensive Environmental, Social, and Governance (ESG) reporting module for Odoo 19, designed to help organizations track, manage, and report on their sustainability performance.

## Features

### Environmental
- **Collected Emissions**: Track carbon emissions from various sources (transportation, equipment, facilities)
- **Offset Emissions**: Manage carbon offset projects and investments
- **Carbon Analytics**: Comprehensive carbon footprint analysis and reporting
- **Emission Factors**: Configurable emission factors for different activities

### Social
- **Employee Community**: Track employee commute emissions and community activities
- **Gender Parity**: Monitor gender distribution, leadership representation, and diversity metrics
- **Pay Gap Analysis**: Analyze salary differences between groups with mean, median, and leadership pay gaps

### Governance
- **ESG Initiatives**: Create and manage sustainability initiatives with progress tracking
- **Impact Assessment**: Measure the impact of ESG initiatives on overall performance
- **Budget Management**: Track budgets and costs associated with ESG activities

## Installation

1. Place the module in your Odoo addons directory
2. Update the addons list in Odoo
3. Install the "ESG Reporting" module
4. Configure user groups and permissions as needed

## Configuration

### User Groups
- **ESG User**: Basic access to view and create ESG records
- **ESG Manager**: Enhanced access to manage and validate ESG data
- **ESG Administrator**: Full access to all ESG features and configuration

### Initial Data
The module includes default data for:
- Emission factors (Grid Electricity, Natural Gas, Diesel, etc.)
- Offset types (Tree Planting, Renewable Energy, etc.)
- Initiative tags (Carbon Reduction, Energy Efficiency, etc.)

## Usage

### Environmental Tracking
1. Navigate to ESG Reporting > Environmental > Collected Emissions
2. Create new emission records with details like source, quantity, and emission factor
3. View emissions in List, Kanban, Graph, or Pivot views
4. Track offset emissions in the Offset Emissions section

### Social Metrics
1. Access Gender Parity under ESG Reporting > Social
2. Enter employee counts by gender and leadership positions
3. View diversity scores and leadership ratios
4. Analyze pay gaps in the Pay Gap section

### Governance
1. Create ESG initiatives under ESG Reporting > Governance
2. Set budgets, timelines, and impact metrics
3. Track progress using Kanban or Calendar views
4. Generate reports on initiative performance

### Analytics and Reporting
1. Access the ESG Dashboard for an overview of key metrics
2. Use the Analytics section for detailed carbon footprint analysis
3. Generate comprehensive ESG reports using the Report Wizard
4. Export data in various formats (PDF, Excel, HTML, JSON)

## Models

### Core Models
- `esg.emission`: Track collected emissions
- `esg.offset`: Manage offset emissions
- `esg.employee.community`: Employee commute and community activities
- `esg.initiative`: ESG initiatives and projects
- `esg.analytics`: Aggregated ESG performance data
- `esg.gender.parity`: Gender distribution and diversity metrics
- `esg.pay.gap`: Pay gap analysis between groups

### Supporting Models
- `esg.emission.factor`: Emission factors for calculations
- `esg.offset.type`: Types of offset projects
- `esg.community.initiative`: Community initiatives
- `esg.initiative.tag`: Tags for categorizing initiatives
- `esg.carbon.footprint`: Detailed carbon footprint records

## Security

The module implements role-based access control with:
- Multi-company data segregation
- User group permissions
- Record-level access rules
- Secure data handling

## Reporting

### Available Reports
- Emissions Report
- Offset Report
- Analytics Report
- Gender Parity Report
- Pay Gap Report
- Initiative Report
- Comprehensive ESG Report

### Report Wizard
Use the ESG Report Wizard to generate customized reports with:
- Date range selection
- Data inclusion options
- Multiple output formats
- Filtering capabilities

## Dashboard

The ESG Dashboard provides:
- Real-time ESG metrics
- Visual data representation
- Key performance indicators
- Recent activity overview

## Technical Details

### Dependencies
- base
- mail
- hr
- account
- purchase
- sale
- stock
- project
- web
- spreadsheet_dashboard

### Assets
- JavaScript: Dashboard functionality using Owl components
- CSS: Custom styling for ESG dashboard
- XML: Dashboard templates

## Development

### Adding New Features
1. Create new models in the `models/` directory
2. Add corresponding views in the `views/` directory
3. Update security rules and access controls
4. Add demo data if needed
5. Update the manifest file

### Customization
The module is designed to be extensible:
- Add new emission factors
- Create custom initiative types
- Extend analytics calculations
- Customize report templates

## Support

For support and customization requests, please contact your Odoo partner or the module developer.

## License

This module is licensed under LGPL-3.

## Version History

- 1.0.0: Initial release with comprehensive ESG tracking and reporting capabilities