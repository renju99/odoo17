from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
import json

_logger = logging.getLogger(__name__)


class ESGFramework(models.Model):
    _name = 'esg.framework'
    _description = 'ESG Framework'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Framework Name',
        required=True,
        tracking=True,
        help="Name of the ESG framework (e.g., GRI, SASB, TCFD)"
    )
    
    code = fields.Char(
        string='Framework Code',
        required=True,
        tracking=True,
        help="Short code for the framework (e.g., GRI, SASB, TCFD)"
    )
    
    framework_type = fields.Selection([
        ('gri', 'GRI (Global Reporting Initiative)'),
        ('sasb', 'SASB (Sustainability Accounting Standards Board)'),
        ('tcfd', 'TCFD (Task Force on Climate-related Financial Disclosures)'),
        ('csrd', 'CSRD (Corporate Sustainability Reporting Directive)'),
        ('cdp', 'CDP (Carbon Disclosure Project)'),
        ('ungc', 'UN Global Compact'),
        ('sdgs', 'UN Sustainable Development Goals'),
        ('custom', 'Custom Framework'),
    ], string='Framework Type', required=True, default='gri')
    
    version = fields.Char(
        string='Version',
        tracking=True,
        help="Framework version (e.g., GRI 2021, SASB 2018)"
    )
    
    description = fields.Text(
        string='Description',
        tracking=True,
        help="Detailed description of the framework"
    )
    
    # Framework Requirements
    materiality_threshold = fields.Float(
        string='Materiality Threshold (%)',
        default=5.0,
        tracking=True,
        help="Materiality threshold for determining significant ESG topics"
    )
    
    reporting_frequency = fields.Selection([
        ('annual', 'Annual'),
        ('semi_annual', 'Semi-Annual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
    ], string='Reporting Frequency', default='annual', tracking=True)
    
    # Compliance Fields
    compliance_status = fields.Selection([
        ('not_applicable', 'Not Applicable'),
        ('planning', 'Planning'),
        ('implementing', 'Implementing'),
        ('compliant', 'Compliant'),
        ('certified', 'Certified'),
    ], string='Compliance Status', default='not_applicable', tracking=True)
    
    compliance_score = fields.Float(
        string='Compliance Score (%)',
        default=0.0,
        tracking=True,
        help="Percentage of framework requirements met"
    )
    
    last_assessment_date = fields.Date(
        string='Last Assessment Date',
        tracking=True
    )
    
    next_assessment_date = fields.Date(
        string='Next Assessment Date',
        tracking=True
    )
    
    # Framework Standards
    standards_ids = fields.One2many(
        'esg.framework.standard',
        'framework_id',
        string='Standards',
        help="Standards within this framework"
    )
    
    # Integration Fields
    auto_collect_data = fields.Boolean(
        string='Auto Collect Data',
        default=True,
        tracking=True,
        help="Automatically collect data for this framework"
    )
    
    data_sources = fields.Text(
        string='Data Sources',
        tracking=True,
        help="List of data sources for this framework"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.constrains('materiality_threshold')
    def _check_materiality_threshold(self):
        for record in self:
            if record.materiality_threshold < 0 or record.materiality_threshold > 100:
                raise ValidationError(_('Materiality threshold must be between 0 and 100.'))
    
    @api.constrains('compliance_score')
    def _check_compliance_score(self):
        for record in self:
            if record.compliance_score < 0 or record.compliance_score > 100:
                raise ValidationError(_('Compliance score must be between 0 and 100.'))
    
    @api.model
    def get_framework_requirements(self, framework_code):
        """Get framework requirements and standards"""
        framework = self.search([('code', '=', framework_code), ('active', '=', True)], limit=1)
        if framework:
            return {
                'framework': framework.read(['name', 'version', 'description', 'materiality_threshold'])[0],
                'standards': framework.standards_ids.read(['name', 'code', 'description', 'category', 'required']),
            }
        return {}
    
    @api.model
    def assess_compliance(self, framework_id):
        """Assess compliance with framework requirements"""
        framework = self.browse(framework_id)
        if not framework.exists():
            return False
        
        # Calculate compliance score based on standards
        standards = framework.standards_ids.filtered(lambda s: s.required)
        if not standards:
            framework.compliance_score = 0.0
            return True
        
        compliant_standards = standards.filtered(lambda s: s.is_compliant)
        compliance_score = (len(compliant_standards) / len(standards)) * 100
        
        framework.write({
            'compliance_score': compliance_score,
            'last_assessment_date': fields.Date.today(),
        })
        
        return True


class ESGFrameworkStandard(models.Model):
    _name = 'esg.framework.standard'
    _description = 'ESG Framework Standard'
    _order = 'framework_id, category, sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Standard Name',
        required=True,
        tracking=True
    )
    
    code = fields.Char(
        string='Standard Code',
        required=True,
        tracking=True,
        help="Standard code (e.g., GRI 103, SASB EN-AC-410a.1)"
    )
    
    framework_id = fields.Many2one(
        'esg.framework',
        string='Framework',
        required=True,
        ondelete='cascade'
    )
    
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('economic', 'Economic'),
        ('general', 'General'),
    ], string='Category', required=True, default='environmental')
    
    subcategory = fields.Char(
        string='Subcategory',
        tracking=True,
        help="Subcategory of the standard"
    )
    
    description = fields.Text(
        string='Description',
        tracking=True
    )
    
    requirements = fields.Text(
        string='Requirements',
        tracking=True,
        help="Detailed requirements for this standard"
    )
    
    required = fields.Boolean(
        string='Required',
        default=True,
        tracking=True,
        help="Whether this standard is required for compliance"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Ordering sequence"
    )
    
    # Compliance Tracking
    is_compliant = fields.Boolean(
        string='Is Compliant',
        default=False,
        tracking=True
    )
    
    compliance_notes = fields.Text(
        string='Compliance Notes',
        tracking=True
    )
    
    last_assessment_date = fields.Date(
        string='Last Assessment Date',
        tracking=True
    )
    
    # Data Mapping
    data_source_model = fields.Char(
        string='Data Source Model',
        tracking=True,
        help="Odoo model that provides data for this standard"
    )
    
    data_source_field = fields.Char(
        string='Data Source Field',
        tracking=True,
        help="Field in the model that provides data"
    )
    
    calculation_method = fields.Text(
        string='Calculation Method',
        tracking=True,
        help="Method for calculating compliance with this standard"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    @api.model
    def assess_standard_compliance(self, standard_id):
        """Assess compliance with a specific standard"""
        standard = self.browse(standard_id)
        if not standard.exists():
            return False
        
        # Check if data source is available
        if standard.data_source_model and standard.data_source_field:
            model = self.env.get(standard.data_source_model)
            if model:
                # Check if data exists for the current period
                domain = []
                if hasattr(model, 'company_id'):
                    domain.append(('company_id', '=', self.env.company.id))
                if hasattr(model, 'date'):
                    current_year = fields.Date.today().year
                    domain.append(('date', '>=', f'{current_year}-01-01'))
                    domain.append(('date', '<=', f'{current_year}-12-31'))
                
                record_count = model.search_count(domain)
                is_compliant = record_count > 0
                
                standard.write({
                    'is_compliant': is_compliant,
                    'last_assessment_date': fields.Date.today(),
                    'compliance_notes': f"Data source check: {record_count} records found" if is_compliant else "No data found for current period"
                })
                
                return True
        
        return False


class ESGMaterialityAssessment(models.Model):
    _name = 'esg.materiality.assessment'
    _description = 'ESG Materiality Assessment'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Assessment Name',
        required=True,
        tracking=True
    )
    
    date = fields.Date(
        string='Assessment Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    framework_id = fields.Many2one(
        'esg.framework',
        string='Framework',
        required=True,
        tracking=True
    )
    
    assessment_type = fields.Selection([
        ('initial', 'Initial Assessment'),
        ('periodic', 'Periodic Review'),
        ('update', 'Update Assessment'),
    ], string='Assessment Type', required=True, default='initial')
    
    # Materiality Matrix
    topics_ids = fields.One2many(
        'esg.materiality.topic',
        'assessment_id',
        string='Materiality Topics'
    )
    
    # Stakeholder Engagement
    stakeholder_engagement = fields.Text(
        string='Stakeholder Engagement',
        tracking=True,
        help="Description of stakeholder engagement process"
    )
    
    stakeholders_consulted = fields.Integer(
        string='Stakeholders Consulted',
        tracking=True
    )
    
    # Assessment Results
    materiality_threshold = fields.Float(
        string='Materiality Threshold',
        default=5.0,
        tracking=True
    )
    
    significant_topics_count = fields.Integer(
        string='Significant Topics Count',
        compute='_compute_significant_topics',
        store=True
    )
    
    assessment_score = fields.Float(
        string='Assessment Score',
        compute='_compute_assessment_score',
        store=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('validated', 'Validated'),
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
    
    @api.depends('topics_ids.impact_score', 'topics_ids.probability_score')
    def _compute_significant_topics(self):
        for record in self:
            significant_topics = record.topics_ids.filtered(
                lambda t: t.impact_score * t.probability_score >= record.materiality_threshold
            )
            record.significant_topics_count = len(significant_topics)
    
    @api.depends('topics_ids.impact_score', 'topics_ids.probability_score')
    def _compute_assessment_score(self):
        for record in self:
            if record.topics_ids:
                total_score = sum(
                    topic.impact_score * topic.probability_score 
                    for topic in record.topics_ids
                )
                record.assessment_score = total_score / len(record.topics_ids)
            else:
                record.assessment_score = 0.0
    
    def action_start_assessment(self):
        self.write({'state': 'in_progress'})
    
    def action_complete_assessment(self):
        self.write({'state': 'completed'})
    
    def action_validate_assessment(self):
        self.write({'state': 'validated'})
    
    def action_draft(self):
        self.write({'state': 'draft'})


class ESGMaterialityTopic(models.Model):
    _name = 'esg.materiality.topic'
    _description = 'ESG Materiality Topic'
    _order = 'sequence'

    name = fields.Char(
        string='Topic Name',
        required=True
    )
    
    assessment_id = fields.Many2one(
        'esg.materiality.assessment',
        string='Assessment',
        required=True,
        ondelete='cascade'
    )
    
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
        ('economic', 'Economic'),
    ], string='Category', required=True, default='environmental')
    
    subcategory = fields.Char(
        string='Subcategory'
    )
    
    description = fields.Text(
        string='Description'
    )
    
    # Materiality Scoring
    impact_score = fields.Float(
        string='Impact Score (1-10)',
        default=5.0,
        help="Impact on stakeholders and business (1-10 scale)"
    )
    
    probability_score = fields.Float(
        string='Probability Score (1-10)',
        default=5.0,
        help="Probability of occurrence (1-10 scale)"
    )
    
    materiality_score = fields.Float(
        string='Materiality Score',
        compute='_compute_materiality_score',
        store=True,
        help="Impact Score × Probability Score"
    )
    
    is_significant = fields.Boolean(
        string='Is Significant',
        compute='_compute_is_significant',
        store=True
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    @api.depends('impact_score', 'probability_score')
    def _compute_materiality_score(self):
        for record in self:
            record.materiality_score = record.impact_score * record.probability_score
    
    @api.depends('materiality_score', 'assessment_id.materiality_threshold')
    def _compute_is_significant(self):
        for record in self:
            threshold = record.assessment_id.materiality_threshold
            record.is_significant = record.materiality_score >= threshold
    
    @api.constrains('impact_score', 'probability_score')
    def _check_scores(self):
        for record in self:
            if record.impact_score < 1 or record.impact_score > 10:
                raise ValidationError(_('Impact score must be between 1 and 10.'))
            if record.probability_score < 1 or record.probability_score > 10:
                raise ValidationError(_('Probability score must be between 1 and 10.'))