from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGEmissions(models.Model):
    _name = 'esg.emission'
    _description = 'ESG Emissions'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Emission Name',
        required=True,
        tracking=True,
        help="Name of the emission source (e.g., Electricity, Transportation)"
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        tracking=True,
        help="Partner responsible for this emission"
    )
    
    emission_factor_id = fields.Many2one(
        'esg.emission.factor',
        string='Emission Factor',
        required=True,
        tracking=True,
        help="Type of emission factor (e.g., Grid Electricity, Transportation)"
    )
    
    quantity = fields.Float(
        string='Quantity',
        required=True,
        tracking=True,
        help="Quantity of the emission source used"
    )
    
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('km', 'km'),
        ('kg', 'kg'),
        ('liter', 'Liter'),
        ('ton', 'Ton'),
        ('m3', 'm³'),
    ], string='Unit', required=True, default='kwh')
    
    emission_amount = fields.Float(
        string='Emission Amount (t CO2)',
        compute='_compute_emission_amount',
        store=True,
        help="Calculated emission amount in tons of CO2"
    )
    
    amount = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        tracking=True,
        help="Cost associated with this emission"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        tracking=True,
        help="Journal for accounting entries"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(
        string='Notes',
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed fields for reporting
    month = fields.Char(
        string='Month',
        compute='_compute_period_fields',
        store=True
    )
    
    year = fields.Integer(
        string='Year',
        compute='_compute_period_fields',
        store=True
    )
    
    @api.depends('quantity', 'emission_factor_id')
    def _compute_emission_amount(self):
        for record in self:
            if record.quantity and record.emission_factor_id:
                record.emission_amount = record.quantity * record.emission_factor_id.factor
            else:
                record.emission_amount = 0.0
    
    @api.depends('date')
    def _compute_period_fields(self):
        for record in self:
            if record.date:
                record.month = record.date.strftime('%B %Y')
                record.year = record.date.year
            else:
                record.month = ''
                record.year = 0
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_validate(self):
        self.write({'state': 'validated'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def get_emission_summary(self, date_from=None, date_to=None):
        """Get emission summary for reporting"""
        domain = [('state', '=', 'validated')]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        emissions = self.search(domain)
        
        return {
            'total_emissions': sum(emissions.mapped('emission_amount')),
            'total_cost': sum(emissions.mapped('amount')),
            'count': len(emissions),
            'by_factor': emissions.read_group(
                domain, 
                ['emission_factor_id', 'emission_amount:sum'], 
                ['emission_factor_id']
            ),
        }
    
    @api.model
    def auto_collect_emission_data(self):
        """Automatically collect emission data from various Odoo modules"""
        _logger.info("Starting automatic emission data collection")
        
        collected_data = {
            'fleet_emissions': 0,
            'manufacturing_emissions': 0,
            'energy_consumption': 0,
            'waste_emissions': 0,
            'records_created': 0
        }
        
        try:
            # 1. Collect from Fleet Module
            if 'fleet.vehicle' in self.env:
                fleet_emissions = self._collect_fleet_emissions()
                collected_data['fleet_emissions'] = fleet_emissions
            
            # 2. Collect from Manufacturing Module
            if 'mrp.production' in self.env:
                manufacturing_emissions = self._collect_manufacturing_emissions()
                collected_data['manufacturing_emissions'] = manufacturing_emissions
            
            # 3. Collect from Energy Consumption (if available)
            energy_emissions = self._collect_energy_consumption()
            collected_data['energy_consumption'] = energy_emissions
            
            # 4. Collect from Waste Management (if available)
            waste_emissions = self._collect_waste_emissions()
            collected_data['waste_emissions'] = waste_emissions
            
            _logger.info(f"Emission data collection completed: {collected_data}")
            return collected_data
            
        except Exception as e:
            _logger.error(f"Error in automatic emission data collection: {e}")
            return collected_data
    
    def _collect_fleet_emissions(self):
        """Collect emissions from fleet vehicles"""
        total_emissions = 0
        fleet_model = self.env.get('fleet.vehicle')
        
        if not fleet_model:
            return total_emissions
        
        # Get fleet vehicles with fuel consumption data
        vehicles = fleet_model.search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ])
        
        for vehicle in vehicles:
            # Calculate emissions based on fuel consumption
            if hasattr(vehicle, 'fuel_consumption') and vehicle.fuel_consumption:
                # Standard emission factors (kg CO2 per liter)
                fuel_emission_factors = {
                    'gasoline': 2.31,
                    'diesel': 2.68,
                    'electric': 0.0,  # Electric vehicles have zero direct emissions
                    'hybrid': 1.5,
                }
                
                fuel_type = getattr(vehicle, 'fuel_type', 'gasoline')
                emission_factor = fuel_emission_factors.get(fuel_type, 2.31)
                
                # Calculate emissions for the current year
                current_year = fields.Date.today().year
                fuel_consumption = vehicle.fuel_consumption or 0
                
                # Estimate annual consumption (this would need to be enhanced with actual data)
                annual_consumption = fuel_consumption * 12  # Monthly average * 12
                emissions = (annual_consumption * emission_factor) / 1000  # Convert to tons
                
                # Create emission record
                emission_factor_record = self.env['esg.emission.factor'].search([
                    ('name', 'ilike', fuel_type)
                ], limit=1)
                
                if not emission_factor_record:
                    emission_factor_record = self.env['esg.emission.factor'].create({
                        'name': f'{fuel_type.title()} Vehicle',
                        'factor': emission_factor / 1000,  # Convert to t CO2 per liter
                        'unit': 'liter',
                        'category': 'transportation'
                    })
                
                # Create emission record
                self.create({
                    'name': f'Fleet Vehicle - {vehicle.name}',
                    'date': fields.Date.today(),
                    'partner_id': vehicle.driver_id.partner_id.id if vehicle.driver_id else False,
                    'emission_factor_id': emission_factor_record.id,
                    'quantity': annual_consumption,
                    'unit': 'liter',
                    'emission_amount': emissions,
                    'amount': 0,  # Cost would need to be calculated separately
                    'state': 'draft',
                    'notes': f'Automatically collected from fleet vehicle {vehicle.name}'
                })
                
                total_emissions += emissions
        
        return total_emissions
    
    def _collect_manufacturing_emissions(self):
        """Collect emissions from manufacturing operations"""
        total_emissions = 0
        mrp_model = self.env.get('mrp.production')
        
        if not mrp_model:
            return total_emissions
        
        # Get manufacturing orders for current year
        current_year = fields.Date.today().year
        productions = mrp_model.search([
            ('date_planned_start', '>=', f'{current_year}-01-01'),
            ('date_planned_start', '<=', f'{current_year}-12-31'),
            ('state', 'in', ['confirmed', 'progress', 'done'])
        ])
        
        for production in productions:
            # Calculate emissions based on production volume and energy consumption
            # This is a simplified calculation - in practice, you'd need more detailed data
            
            # Estimate energy consumption based on production quantity
            if production.product_qty:
                # Rough estimate: 1 kWh per unit produced
                energy_consumption = production.product_qty * 1  # kWh
                
                # Electricity emission factor (kg CO2 per kWh)
                electricity_factor = 0.5  # This varies by region
                emissions = (energy_consumption * electricity_factor) / 1000  # Convert to tons
                
                # Create emission record
                emission_factor_record = self.env['esg.emission.factor'].search([
                    ('name', 'ilike', 'electricity')
                ], limit=1)
                
                if not emission_factor_record:
                    emission_factor_record = self.env['esg.emission.factor'].create({
                        'name': 'Manufacturing Electricity',
                        'factor': electricity_factor / 1000,  # Convert to t CO2 per kWh
                        'unit': 'kwh',
                        'category': 'electricity'
                    })
                
                self.create({
                    'name': f'Manufacturing - {production.product_id.name}',
                    'date': production.date_planned_start,
                    'emission_factor_id': emission_factor_record.id,
                    'quantity': energy_consumption,
                    'unit': 'kwh',
                    'emission_amount': emissions,
                    'amount': 0,
                    'state': 'draft',
                    'notes': f'Automatically collected from manufacturing order {production.name}'
                })
                
                total_emissions += emissions
        
        return total_emissions
    
    def _collect_energy_consumption(self):
        """Collect emissions from energy consumption"""
        total_emissions = 0
        
        # This would integrate with energy management systems
        # For now, we'll create a placeholder for manual entry
        
        # Check if we have any energy consumption records
        energy_consumption = self.search([
            ('emission_factor_id.category', '=', 'electricity'),
            ('date', '>=', f'{fields.Date.today().year}-01-01')
        ])
        
        if not energy_consumption:
            # Create a placeholder for energy consumption
            emission_factor_record = self.env['esg.emission.factor'].search([
                ('name', 'ilike', 'electricity')
            ], limit=1)
            
            if not emission_factor_record:
                emission_factor_record = self.env['esg.emission.factor'].create({
                    'name': 'Grid Electricity',
                    'factor': 0.5 / 1000,  # kg CO2 per kWh converted to t CO2 per kWh
                    'unit': 'kwh',
                    'category': 'electricity'
                })
            
            # Create a placeholder record for energy consumption
            self.create({
                'name': 'Energy Consumption - Placeholder',
                'date': fields.Date.today(),
                'emission_factor_id': emission_factor_record.id,
                'quantity': 0,
                'unit': 'kwh',
                'emission_amount': 0,
                'amount': 0,
                'state': 'draft',
                'notes': 'Placeholder for energy consumption data - please update with actual values'
            })
        
        return total_emissions
    
    def _collect_waste_emissions(self):
        """Collect emissions from waste management"""
        total_emissions = 0
        
        # This would integrate with waste management systems
        # For now, we'll create a placeholder
        
        waste_emission_factor = self.env['esg.emission.factor'].search([
            ('name', 'ilike', 'waste')
        ], limit=1)
        
        if not waste_emission_factor:
            waste_emission_factor = self.env['esg.emission.factor'].create({
                'name': 'Waste Disposal',
                'factor': 0.5,  # kg CO2 per kg of waste
                'unit': 'kg',
                'category': 'waste'
            })
        
        # Create a placeholder record for waste emissions
        self.create({
            'name': 'Waste Emissions - Placeholder',
            'date': fields.Date.today(),
            'emission_factor_id': waste_emission_factor.id,
            'quantity': 0,
            'unit': 'kg',
            'emission_amount': 0,
            'amount': 0,
            'state': 'draft',
            'notes': 'Placeholder for waste emissions data - please update with actual values'
        })
        
        return total_emissions


class ESGEmissionFactor(models.Model):
    _name = 'esg.emission.factor'
    _description = 'ESG Emission Factor'
    _order = 'name'

    name = fields.Char(
        string='Factor Name',
        required=True,
        help="Name of the emission factor (e.g., Grid Electricity, Car Transportation)"
    )
    
    factor = fields.Float(
        string='Emission Factor (t CO2/unit)',
        required=True,
        help="Emission factor in tons of CO2 per unit"
    )
    
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('km', 'km'),
        ('kg', 'kg'),
        ('liter', 'Liter'),
        ('ton', 'Ton'),
        ('m3', 'm³'),
    ], string='Unit', required=True, default='kwh')
    
    category = fields.Selection([
        ('electricity', 'Electricity'),
        ('transportation', 'Transportation'),
        ('heating', 'Heating'),
        ('waste', 'Waste'),
        ('water', 'Water'),
        ('other', 'Other'),
    ], string='Category', required=True, default='electricity')
    
    description = fields.Text(
        string='Description',
        help="Detailed description of the emission factor"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    @api.constrains('factor')
    def _check_factor(self):
        for record in self:
            if record.factor < 0:
                raise ValidationError(_('Emission factor cannot be negative.'))