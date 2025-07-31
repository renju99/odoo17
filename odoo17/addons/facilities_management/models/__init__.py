# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# ===============================
# Import all models in dependency order
# ===============================

# 1. Base/Configuration/Lookup Models (Least dependencies within module)
from . import hr_employee
from . import product
from . import maintenance_team
# maintenance_job_plan_task is defined in maintenance_job_plan.py, so don't import separately
from . import maintenance_job_plan    # Loads both job plan and its tasks

# 2. Core Infrastructure & Assets (Hierarchical, depends on basic Odoo models)
from . import building
from . import floor
from . import room
from . import facility
from . import asset_category
from . import asset
from . import workorder_permit
from . import space_booking
from . import booking_template
from . import room_equipment
from . import booking_reject_wizard

# 3. Asset Performance (depends on asset)
from . import asset_performance

# 4. Transactional Models (Depend on many of the above)
from . import maintenance_workorder
from . import maintenance_workorder_assignment
from . import maintenance_workorder_part_line
from . import maintenance_workorder_task
from . import maintenance_job_plan_section
from . import maintenance_job_plan_task
from . import maintenance_job_plan
from . import maintenance_workorder_section
from . import stock_picking

# 5. Scheduled/Predictive Maintenance (Often depend on assets and work orders)
from . import asset_maintenance_schedule
from . import predictive_maintenance
from . import asset_depreciation

# SLA and Resource Utilization (NEW)
from . import sla
from . import workorder_sla
from . import resource_utilization
from . import sla_analytics
from . import workorder_sla_integration

# IoT and Smart Asset Models (NEW)
from . import asset_sensor
from . import asset_threshold
from . import asset_scan_wizard
from . import asset_disposal_wizard
from . import facilities_import_wizard

# Other integration/utilities
from . import ir_websocket

# ===============================
# Hooks
# ===============================

def pre_init_hook(cr):
    """Ensure clean slate for facilities_management module."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Running pre_init_hook for facilities_management...")
    try:
        cr.execute("""
            DELETE FROM ir_model WHERE model = 'facilities.facility';
            DELETE FROM ir_model_data WHERE model = 'ir.model' AND name LIKE 'model_facilities%';
        """)
        _logger.info("Cleaned up old facilities.facility model entries (if any).")
    except Exception as e:
        _logger.warning(f"Failed to run pre_init_hook cleanup: {e}")

def post_init_hook(env):
    """Ensure at least one SLA record exists for foreign key sanity."""
    env['facilities.sla'].create_default_sla_records()
    _logger.info("Ensured default SLA records exist after install/upgrade.")