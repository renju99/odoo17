from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ESGReportWizard(models.TransientModel):
    _name = 'esg.report.wizard'
    _description = 'ESG Report Wizard'

    name = fields.Char(
        string='Report Name',
        required=True,
        help="Name of the ESG report"
    )
    
    report_type = fields.Selection([
        ('comprehensive', 'Comprehensive ESG Report'),
        ('environmental', 'Environmental Report'),
        ('social', 'Social Report'),
        ('governance', 'Governance Report'),
        ('carbon_analytics', 'Carbon Analytics Report'),
        ('gender_parity', 'Gender Parity Report'),
        ('pay_gap', 'Pay Gap Report'),
        ('initiatives', 'Initiatives Report'),
    ], string='Report Type', required=True, default='comprehensive')
    
    date_from = fields.Date(
        string='Date From',
        required=True,
        default=fields.Date.today,
        help="Start date for the report period"
    )
    
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today,
        help="End date for the report period"
    )
    
    include_emissions = fields.Boolean(
        string='Include Emissions Data',
        default=True,
        help="Include carbon emissions data in the report"
    )
    
    include_offsets = fields.Boolean(
        string='Include Offset Data',
        default=True,
        help="Include carbon offset data in the report"
    )
    
    include_community = fields.Boolean(
        string='Include Community Data',
        default=True,
        help="Include employee community data in the report"
    )
    
    include_initiatives = fields.Boolean(
        string='Include Initiatives Data',
        default=True,
        help="Include ESG initiatives data in the report"
    )
    
    include_gender_parity = fields.Boolean(
        string='Include Gender Parity Data',
        default=True,
        help="Include gender parity data in the report"
    )
    
    include_pay_gap = fields.Boolean(
        string='Include Pay Gap Data',
        default=True,
        help="Include pay gap data in the report"
    )
    
    include_analytics = fields.Boolean(
        string='Include Analytics Data',
        default=True,
        help="Include analytics data in the report"
    )
    
    format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
        ('json', 'JSON'),
    ], string='Output Format', required=True, default='pdf')
    
    include_charts = fields.Boolean(
        string='Include Charts',
        default=True,
        help="Include charts and graphs in the report"
    )
    
    include_summary = fields.Boolean(
        string='Include Executive Summary',
        default=True,
        help="Include executive summary in the report"
    )
    
    include_recommendations = fields.Boolean(
        string='Include Recommendations',
        default=True,
        help="Include recommendations in the report"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('Date From cannot be after Date To.'))
    
    def action_generate_report(self):
        """Generate the ESG report based on selected parameters"""
        self.ensure_one()
        
        # Collect data based on report type and selected options
        report_data = self._collect_report_data()
        
        # Generate report based on format
        if self.format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif self.format == 'excel':
            return self._generate_excel_report(report_data)
        elif self.format == 'html':
            return self._generate_html_report(report_data)
        elif self.format == 'json':
            return self._generate_json_report(report_data)
    
    def _collect_report_data(self):
        """Collect data for the report based on selected options"""
        data = {
            'report_info': {
                'name': self.name,
                'type': self.report_type,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'company': self.company_id.name,
                'generated_date': fields.Date.today(),
            },
            'emissions': {},
            'offsets': {},
            'community': {},
            'initiatives': {},
            'gender_parity': {},
            'pay_gap': {},
            'analytics': {},
        }
        
        # Collect emissions data
        if self.include_emissions:
            data['emissions'] = self.env['esg.emission'].get_emission_summary(
                self.date_from, self.date_to
            )
        
        # Collect offset data
        if self.include_offsets:
            data['offsets'] = self.env['esg.offset'].get_offset_summary(
                self.date_from, self.date_to
            )
        
        # Collect community data
        if self.include_community:
            data['community'] = self.env['esg.employee.community'].get_community_summary(
                self.date_from, self.date_to
            )
        
        # Collect initiatives data
        if self.include_initiatives:
            data['initiatives'] = self.env['esg.initiative'].get_initiative_summary(
                self.date_from, self.date_to
            )
        
        # Collect gender parity data
        if self.include_gender_parity:
            data['gender_parity'] = self.env['esg.gender.parity'].get_gender_parity_summary(
                self.date_from, self.date_to
            )
        
        # Collect pay gap data
        if self.include_pay_gap:
            data['pay_gap'] = self.env['esg.pay.gap'].get_pay_gap_summary(
                self.date_from, self.date_to
            )
        
        # Collect analytics data
        if self.include_analytics:
            data['analytics'] = self.env['esg.analytics'].get_analytics_summary(
                self.date_from, self.date_to
            )
        
        return data
    
    def _get_analytics_type_mapping(self):
        """Get mapping from wizard report types to analytics types"""
        return {
            'comprehensive': 'esg_performance',
            'environmental': 'carbon_analytics',
            'social': 'esg_performance',
            'governance': 'esg_performance',
            'carbon_analytics': 'carbon_analytics',
            'gender_parity': 'esg_performance',
            'pay_gap': 'esg_performance',
            'initiatives': 'esg_performance',
        }
    
    def _create_analytics_record(self, data):
        """Create an analytics record with proper type mapping"""
        analytics_type_mapping = self._get_analytics_type_mapping()
        return self.env['esg.analytics'].create({
            'name': self.name,
            'date': fields.Date.today(),
            'analytics_type': analytics_type_mapping.get(self.report_type, 'esg_performance'),
            'period_type': 'monthly',  # Use monthly as default since 'custom' is not available
            'date_from': self.date_from,
            'date_to': self.date_to,
            'state': 'completed',
            'report_data': str(data),  # Store the data as JSON string
        })
    
    def _generate_pdf_report(self, data):
        """Generate PDF report"""
        # Create a temporary record to pass data to the report
        report_record = self._create_analytics_record(data)
        
        # Return the report action
        return {
            'type': 'ir.actions.report',
            'report_name': 'esg_reporting.report_esg_comprehensive',
            'report_type': 'qweb-pdf',
            'context': {
                'active_ids': [report_record.id],
                'active_model': 'esg.analytics',
            }
        }
    
    def _generate_excel_report(self, data):
        """Generate Excel report"""
        # For Excel reports, we'll create a downloadable file
        import base64
        import json
        
        # Convert data to JSON for Excel export
        json_data = json.dumps(data, default=str)
        excel_content = base64.b64encode(json_data.encode('utf-8'))
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.name}.json',
            'type': 'binary',
            'datas': excel_content,
            'res_model': self._name,
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def _generate_html_report(self, data):
        """Generate HTML report"""
        # Create a temporary record to pass data to the report
        report_record = self._create_analytics_record(data)
        
        # Return the report action for HTML
        return {
            'type': 'ir.actions.report',
            'report_name': 'esg_reporting.report_esg_comprehensive',
            'report_type': 'qweb-html',
            'context': {
                'active_ids': [report_record.id],
                'active_model': 'esg.analytics',
            }
        }
    
    def _generate_json_report(self, data):
        """Generate JSON report"""
        import base64
        import json
        
        # Convert data to JSON
        json_data = json.dumps(data, default=str, indent=2)
        json_content = base64.b64encode(json_data.encode('utf-8'))
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.name}.json',
            'type': 'binary',
            'datas': json_content,
            'res_model': self._name,
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }