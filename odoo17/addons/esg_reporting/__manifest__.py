{
    'name': 'Facilities Management Module',
    'version': '1.0',
    'category': 'Facilities Management',
    'summary': 'Enhanced ESG Reporting and Analytics',
    'description': """
        Enhanced ESG Reporting and Analytics Module
        This module provides comprehensive ESG reporting capabilities including:

        - Advanced Report Types (Sustainability, Compliance, Risk Assessment, etc.)
        - Enhanced Analytics (Predictive, Correlation, Anomaly Detection)
        - Interactive Dashboards
        - Multiple Output Formats (PDF, Excel, HTML, JSON, CSV)
        - Custom Configuration Options
        - Threshold Monitoring and Alerts
        - Trend Analysis and Forecasting
        - Benchmarking and Best Practices
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'hr',
        'account',
        'purchase',
        'sale',
        'stock',
        'project',
        'web',
        'spreadsheet_dashboard',
        'facilities_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_views.xml',
        'views/asset_certification_views.xml',
        'views/esg_report_wizard_views.xml',
        'views/enhanced_esg_wizard_views.xml',
        'views/enhanced_esg_dashboard_views.xml',
        'views/esg_analytics_views.xml',
        'views/esg_report_menus.xml',
        'reports/esg_report_pdf.xml',
        'reports/enhanced_esg_report_pdf.xml',
        'demo/esg_demo_data.xml',
    ],
    'demo': [
        'demo/esg_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}