{
    'name': 'Facilities Management',
    'version': '17.0.1.0.0',
    'category': 'Services/Facilities',
    'summary': 'Manage facility assets and operations',
    'description': """
        Facilities Management Module
        ===========================
        
        This module provides functionality to manage:
        - Facility assets
        - Asset disposal operations
        - Facility configuration
        - Reports
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/facility_views.xml',
        'views/asset_views.xml',
        'views/asset_disposal_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}