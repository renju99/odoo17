{
    'name': 'ESG Reporting and Analytics',
    'version': '1.0',
    'category': 'Reporting',
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
    ],
    'data': [
        'security/esg_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/esg_offset_views.xml',
        'views/esg_emission_views.xml',
        'views/esg_employee_community_views.xml',
        'views/esg_gender_parity_views.xml',
        'views/esg_initiative_views.xml',
        'views/esg_framework_views.xml',
        'views/esg_pay_gap_views.xml',
        'views/esg_target_views.xml',
        'views/esg_analytics_views.xml',
        'views/esg_dashboard_views.xml',
        'views/enhanced_esg_wizard_views.xml',
        'views/esg_menu_views.xml',
        'views/esg_report_menus.xml',
        'report/esg_reports.xml',
        'report/esg_report_templates.xml',
        'data/esg_data.xml',
        'data/esg_demo.xml',
    ],
    'demo': [
        'data/esg_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}