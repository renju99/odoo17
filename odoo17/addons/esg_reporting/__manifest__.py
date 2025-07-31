{
    'name': 'ESG Reporting',
    'version': '1.0.0',
    'category': 'Sustainability',
    'summary': 'Environmental, Social, and Governance Reporting Module',
    'description': """
        Comprehensive ESG (Environmental, Social, and Governance) reporting module for Odoo 19.
        
        Features:
        - Carbon Emissions Tracking (Collected and Offset)
        - Employee Community and Commute Tracking
        - ESG Initiatives Management
        - Carbon Analytics and Footprint Reporting
        - Gender Parity and Pay Gap Analysis
        - Sustainability Metrics Dashboard
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
        'web_dashboard',
        'spreadsheet_dashboard',
    ],
    'data': [
        'security/esg_security.xml',
        'security/ir.model.access.csv',
        'data/esg_data.xml',
        'views/esg_emission_views.xml',
        'views/esg_offset_views.xml',
        'views/esg_employee_community_views.xml',
        'views/esg_initiative_views.xml',
        'views/esg_analytics_views.xml',
        'views/esg_gender_parity_views.xml',
        'views/esg_pay_gap_views.xml',
        'views/esg_dashboard_views.xml',
        'views/esg_menu_views.xml',
        'report/esg_reports.xml',
        'report/esg_report_templates.xml',
    ],
    'demo': [
        'data/esg_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
                'assets': {
                'web.assets_backend': [
                    'esg_reporting/static/src/js/esg_dashboard.js',
                    'esg_reporting/static/src/css/esg_dashboard.css',
                    'esg_reporting/static/src/xml/esg_dashboard.xml',
                ],
            },
}