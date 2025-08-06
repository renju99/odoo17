{
    'name': 'Facilities Management',
    'version': '1.0.0',
    'summary': 'Comprehensive Facility and Asset Management including Maintenance, Bookings, and Analytics',
    'description': """
Facility and Asset Management System

Features:
- Facilities, Buildings, Floors, Rooms with Google Maps integration
- Asset lifecycle tracking and depreciation with IoT monitoring
- Maintenance scheduling (preventive, corrective, predictive)
- Work order management, assignments, and SLAs
- Resource utilization and technician workload
- Space/Room booking system with conflict detection
- Real-time IoT sensor monitoring and condition-based triggers
- Mobile asset scanning with barcode/RFID support
- Bulk import/export functionality for CSV/Excel
- Advanced analytics and reporting
- Email notifications and reminders
- Mobile and portal views
""",
    'author': 'Your Name or Company',
    'website': 'https://yourcompany.com',
    'category': 'Operations/Facility Management',
    'depends': [
        'base',
        'mail',
        'hr',
        'product',
        'stock',
        'web',
    ],
    'data': [
        # Security
        'security/facility_management_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequences.xml',
        'data/email_templates.xml',
        'data/maintenance_cron.xml',
        'data/predictive_parameters.xml',
        'data/space_booking_mail_template.xml',
        'data/space_booking_data.xml',
        'data/space_booking_enhanced_data.xml',
        'data/iot_sensor_cron.xml',
        'data/asset_threshold_cron.xml',

        # Reports
        'reports/maintenance_report.xml',
        'reports/monthly_building_report_pdf.xml',
        'reports/monthly_building_report_pdf_action.xml',
        'reports/workorder_maintenance_report.xml',

        # Demo
        'demo/facility_demo.xml',

        # Views - Core Facilities
        'views/facility_views.xml',
        'views/building_views.xml',
        'views/floor_views.xml',
        'views/room_views.xml',

        # Views - Assets
        'views/asset_calendar_views.xml',
        'views/facility_asset_menus.xml',
        'views/facility_asset_views.xml',
        'views/asset_category_views.xml',
        'views/asset_dashboard_views.xml',
        'views/asset_performance_views.xml',
        'views/asset_maintenance_schedule_views.xml',
        'views/asset_maintenance_calendar_views.xml',
        'views/asset_maintenance_scheduled_actions.xml',

        # Views - IoT and Smart Assets
        'views/asset_sensor_views.xml',
        'views/asset_scan_wizard_views.xml',
        'views/asset_disposal_wizard_views.xml',
        'views/facilities_import_wizard_views.xml',

        # Views - Maintenance
        'views/maintenance_team_views.xml',
        'views/maintenance_workorder_views.xml',
        'views/maintenance_workorder_part_line_views.xml',
        'views/maintenance_workorder_permit_views.xml',
        'views/maintenance_workorder_kanban.xml',
        'views/maintenance_workorder_mobile_form.xml',
        'views/maintenance_job_plan_views.xml',
        'views/maintenance_report_views.xml',
        'views/maintenance_workorder_calendar_views.xml',

        # Views - Other
        'views/sla_views.xml',
        'views/stock_picking_inherit_views.xml',
        'views/assign_technician_wizard_view.xml',
        'views/space_booking_views.xml',
        'views/space_booking_analytics_views.xml',
        'views/booking_template_views.xml',
        'views/room_equipment_views.xml',
        'views/booking_reject_wizard_views.xml',
        'views/facility_asset_search.xml',
        'views/monthly_building_report_wizard_action.xml',
        'views/monthly_building_report_wizard_view.xml',
        'wizard/sla_deactivation_wizard_views.xml',
        'views/technician_performance_dashboard_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_employee_tree_technician.xml',
        'views/product_views.xml',
    ],
    'demo': [
        'demo/facility_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'facilities_management/static/src/css/facilities.css',
            'facilities_management/static/src/css/portal.css',
            'facilities_management/static/src/js/dashboard_widgets.js',
            'facilities_management/static/src/js/iot_monitoring.js',
            'facilities_management/static/src/js/mobile_scanner.js',
            'facilities_management/static/src/xml/*.xml',
        ],
        'web.assets_frontend': [
            # Add portal/frontend assets here if needed
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}