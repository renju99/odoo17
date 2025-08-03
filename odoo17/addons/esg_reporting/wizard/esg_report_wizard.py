from odoo import models, fields, api
from datetime import timedelta
import json
import logging
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

# Constants for ESG Reporting
DEFAULT_CARBON_THRESHOLD = 1000.0
DEFAULT_COMPLIANCE_THRESHOLD = 90.0
DEFAULT_SOCIAL_IMPACT_THRESHOLD = 7.0
MAX_DATE_RANGE_DAYS = 365 * 5  # 5 years maximum
MIN_DATE_RANGE_DAYS = 1  # 1 day minimum

_logger = logging.getLogger(__name__)


class ESGReportWizard(models.TransientModel):
    _name = 'esg.report.wizard'
    _description = 'ESG Report Wizard'

    name = fields.Char(string='Report Name', required=True, default='ESG Report')
    report_type = fields.Selection([
        ('sustainability', 'Sustainability Report'),
        ('compliance', 'Compliance Report'),
        ('performance', 'Performance Report')
    ], string='Report Type', required=True, default='sustainability')
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML')
    ], string='Format', default='pdf', required=True)

    # Report content options
    include_charts = fields.Boolean(string='Include Charts', default=True)
    include_summary = fields.Boolean(string='Include Summary', default=True)
    include_recommendations = fields.Boolean(string='Include Recommendations', default=True)

    # Data inclusion options
    include_emissions = fields.Boolean(string='Include Emissions', default=True)
    include_offsets = fields.Boolean(string='Include Offsets', default=True)
    include_community = fields.Boolean(string='Include Community', default=True)
    include_initiatives = fields.Boolean(string='Include Initiatives', default=True)
    include_gender_parity = fields.Boolean(string='Include Gender Parity', default=True)
    include_pay_gap = fields.Boolean(string='Include Pay Gap', default=True)
    include_analytics = fields.Boolean(string='Include Analytics', default=True)

    # Company field for multi-company support
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        """Validate date range"""
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_('Date From cannot be later than Date To.'))

                date_diff = (record.date_to - record.date_from).days
                if date_diff > MAX_DATE_RANGE_DAYS:
                    raise ValidationError(
                        _('Date range cannot exceed %d days. Current range: %d days.')
                        % (MAX_DATE_RANGE_DAYS, date_diff)
                    )
                elif date_diff < 0:
                    raise ValidationError(_('Invalid date range.'))

    @api.constrains('name')
    def _check_report_name(self):
        """Validate report name"""
        for record in self:
            if record.name and len(record.name.strip()) < 3:
                raise ValidationError(_('Report name must be at least 3 characters long.'))

    def action_generate_report(self):
        """Generate ESG report with enhanced error handling"""
        try:
            # Validate inputs before processing
            if not self.name or not self.name.strip():
                raise UserError(_('Report name is required.'))

            if not self.date_from or not self.date_to:
                raise UserError(_('Both date from and date to are required.'))

            # Create enhanced wizard with same parameters
            enhanced_wizard = self.env['enhanced.esg.wizard'].create({
                'report_name': self.name,
                'report_type': self.report_type,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'output_format': self.format,
                'include_charts': self.include_charts,
                'include_executive_summary': self.include_summary,
                'include_recommendations': self.include_recommendations,
                'include_emissions_data': self.include_emissions,
                'include_offset_data': self.include_offsets,
                'include_community_data': self.include_community,
                'include_initiatives_data': self.include_initiatives,
                'include_gender_parity_data': self.include_gender_parity,
                'include_pay_gap_data': self.include_pay_gap,
                'include_analytics_data': self.include_analytics,
            })

            # Call the enhanced wizard's action
            return enhanced_wizard.action_generate_enhanced_esg_report()

        except Exception as e:
            _logger.error(f"Error in ESG report generation: {str(e)}")
            raise UserError(_('Failed to generate ESG report: %s') % str(e))


class EnhancedESGWizard(models.TransientModel):
    _name = 'enhanced.esg.wizard'
    _description = 'Enhanced ESG Report Wizard'

    # Basic Configuration
    report_name = fields.Char(string='Report Name', required=True, default='Enhanced ESG Report')
    report_type = fields.Selection([
        ('sustainability', 'Sustainability Performance Report'),
        ('compliance', 'Regulatory Compliance Report'),
        ('risk_assessment', 'ESG Risk Assessment Report'),
        ('performance_analytics', 'Performance Analytics Report'),
        ('trend_analysis', 'Trend Analysis Report'),
        ('benchmarking', 'Benchmarking Report'),
        ('custom', 'Custom Report')
    ], string='Report Type', required=True, default='sustainability')

    # Date Range with Granularity
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    granularity = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Data Granularity', default='monthly')

    # Asset Filtering
    asset_type = fields.Selection([
        ('all', 'All Assets'),
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('it', 'IT Hardware'),
        ('building', 'Building Component'),
        ('infrastructure', 'Infrastructure'),
        ('tool', 'Tool'),
        ('other', 'Other')
    ], string='Asset Type', default='all')

    include_compliance_only = fields.Boolean(string='Include ESG Compliance Assets Only', default=False)

    # Advanced Analytics Options
    include_predictive_analysis = fields.Boolean(string='Include Predictive Analytics', default=False)
    include_correlation_analysis = fields.Boolean(string='Include Correlation Analysis', default=False)
    include_anomaly_detection = fields.Boolean(string='Include Anomaly Detection', default=False)
    include_advanced_analytics = fields.Boolean(string='Include Advanced Analytics', default=False)

    # Report Content Options
    include_charts = fields.Boolean(string='Include Charts and Graphs', default=True, help='Include charts and graphs in the ESG report')
    include_executive_summary = fields.Boolean(string='Include Executive Summary', default=True, help='Include executive summary section in the ESG report')
    include_recommendations = fields.Boolean(string='Include Recommendations', default=True, help='Include recommendations section in the ESG report')
    include_benchmarks = fields.Boolean(string='Include Industry Benchmarks', default=False)
    include_risk_analysis = fields.Boolean(string='Include Risk Analysis', default=False)
    include_trends = fields.Boolean(string='Include Trend Analysis', default=True)
    include_forecasting = fields.Boolean(string='Include Forecasting', default=False)

    # Data Inclusion Options
    include_emissions_data = fields.Boolean(string='Include Emissions Data', default=True)
    include_offset_data = fields.Boolean(string='Include Offset Data', default=True)
    include_community_data = fields.Boolean(string='Include Community Data', default=True)
    include_initiatives_data = fields.Boolean(string='Include Initiatives Data', default=True)
    include_gender_parity_data = fields.Boolean(string='Include Gender Parity Data', default=True)
    include_pay_gap_data = fields.Boolean(string='Include Pay Gap Data', default=True)
    include_analytics_data = fields.Boolean(string='Include Analytics Data', default=True)

    # Report Sections
    include_section_environmental = fields.Boolean(string='Environmental Section', default=True)
    include_section_social = fields.Boolean(string='Social Section', default=True)
    include_section_governance = fields.Boolean(string='Governance Section', default=True)
    include_section_analytics = fields.Boolean(string='Analytics Section', default=True)
    include_section_recommendations = fields.Boolean(string='Recommendations Section', default=True)

    # Comparison Period
    comparison_period = fields.Selection([
        ('none', 'No Comparison'),
        ('previous_period', 'Previous Period'),
        ('same_period_last_year', 'Same Period Last Year'),
        ('custom', 'Custom Period')
    ], string='Comparison Period', default='previous_period')

    custom_comparison_from = fields.Date(string='Custom Comparison From')
    custom_comparison_to = fields.Date(string='Custom Comparison To')

    # Thresholds and Alerts
    include_thresholds = fields.Boolean(string='Include Performance Thresholds', default=False)
    carbon_threshold = fields.Float(string='Carbon Footprint Threshold (kg CO2)',
                                    default=DEFAULT_CARBON_THRESHOLD)
    compliance_threshold = fields.Float(string='Compliance Rate Threshold (%)',
                                        default=DEFAULT_COMPLIANCE_THRESHOLD)
    social_impact_threshold = fields.Float(string='Social Impact Score Threshold',
                                           default=DEFAULT_SOCIAL_IMPACT_THRESHOLD)

    # Report Styling
    report_theme = fields.Selection([
        ('default', 'Default'),
        ('corporate', 'Corporate'),
        ('sustainability', 'Sustainability'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal')
    ], string='Report Theme', default='sustainability')

    include_logo = fields.Boolean(string='Include Company Logo', default=True)
    include_footer = fields.Boolean(string='Include Footer', default=True)

    # Output Format
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('csv', 'CSV')
    ], string='Output Format', default='pdf', required=True)

    # Custom Configuration
    custom_metrics = fields.Text(string='Custom Metrics (JSON)', help='Define custom metrics in JSON format')
    custom_charts = fields.Text(string='Custom Charts (JSON)', help='Define custom charts in JSON format')

    # Company Information
    company_name = fields.Char(string='Company', default='YourCompany')

    # Report data storage for template access
    report_data = fields.Json(string='Report Data', readonly=True, default={})

    @api.depends('report_data')
    def _compute_safe_report_data(self):
        """Computed field to ensure safe access to report data"""
        for record in self:
            try:
                if record.report_data and isinstance(record.report_data, dict):
                    record.safe_report_data = record.report_data
                else:
                    record.safe_report_data = {}
            except Exception:
                record.safe_report_data = {}

    def _compute_safe_report_data_manual(self):
        """Manual computation of safe_report_data for template access"""
        try:
            # Ensure self is a valid record
            if not self or not hasattr(self, 'id') or not self.id:
                return self._get_default_report_data() if self else {}

            # Check if report_data exists and is valid
            if hasattr(self, 'report_data') and self.report_data and isinstance(self.report_data, dict):
                return self.report_data
            else:
                # Try to generate report data if not available
                try:
                    # Get assets and generate report data
                    domain = self._build_asset_domain()
                    assets = self.env['facilities.asset'].search(domain)
                    
                    if not assets:
                        assets = self._get_fallback_assets(domain)
                    
                    report_data = self._prepare_enhanced_report_data(assets)
                    serialized_data = self._serialize_report_data(report_data)
                    
                    if serialized_data and isinstance(serialized_data, dict):
                        return serialized_data
                    else:
                        return self._get_default_report_data()
                except Exception as e:
                    _logger.error(f"Error generating report data in _compute_safe_report_data_manual: {str(e)}")
                    return self._get_default_report_data()
        except Exception as e:
            # Log the error for debugging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in _compute_safe_report_data_manual: {str(e)}")
            return self._get_default_report_data()

    def _compute_safe_report_data_manual_simple(self):
        """Simplified version for template access that always returns valid data"""
        try:
            return self._compute_safe_report_data_manual()
        except Exception:
            return self._get_default_report_data()

    def _get_default_report_data(self):
        """Get default report data structure"""
        try:
            if not self:
                return self._get_ultimate_fallback_data()
            
            return {
                'report_info': {
                    'name': getattr(self, 'report_name', 'ESG Report') if hasattr(self, 'report_name') else 'ESG Report',
                    'type': getattr(self, 'report_type', 'sustainability') if hasattr(self, 'report_type') else 'sustainability',
                    'date_from': getattr(self, 'date_from', None) if hasattr(self, 'date_from') else None,
                    'date_to': getattr(self, 'date_to', None) if hasattr(self, 'date_to') else None,
                    'company': getattr(self, 'company_name', 'YourCompany') if hasattr(self, 'company_name') else 'YourCompany',
                    'generated_at': fields.Datetime.now().isoformat(),
                    'total_assets': 0,
                    'granularity': getattr(self, 'granularity', 'monthly') if hasattr(self, 'granularity') else 'monthly',
                    'theme': getattr(self, 'report_theme', 'default') if hasattr(self, 'report_theme') else 'default',
                    'note': 'Report data not available. Please regenerate the report.'
                },
                'environmental_metrics': {},
                'social_metrics': {},
                'governance_metrics': {},
                'analytics': {},
                'trends': {},
                'benchmarks': {},
                'risk_analysis': {},
                'predictions': {},
                'recommendations': [
                    {'category': 'data', 'recommendation': 'Report data not available. Please regenerate the report.'}
                ],
                'thresholds': {},
                'custom_metrics': {},
                'comparison_data': {}
            }
        except Exception:
            # Ultimate fallback
            return self._get_ultimate_fallback_data()

    def _get_ultimate_fallback_data(self):
        """Get ultimate fallback data when all else fails"""
        return {
            'report_info': {
                'name': 'ESG Report',
                'type': 'sustainability',
                'date_from': None,
                'date_to': None,
                'company': 'YourCompany',
                'generated_at': fields.Datetime.now().isoformat(),
                'total_assets': 0,
                'granularity': 'monthly',
                'theme': 'default',
                'note': 'Report data not available. Please regenerate the report.'
            },
            'environmental_metrics': {},
            'social_metrics': {},
            'governance_metrics': {},
            'analytics': {},
            'trends': {},
            'benchmarks': {},
            'risk_analysis': {},
            'predictions': {},
            'recommendations': [
                {'category': 'data', 'recommendation': 'Report data not available. Please regenerate the report.'}
            ],
            'thresholds': {},
            'custom_metrics': {},
            'comparison_data': {}
        }

    safe_report_data = fields.Json(string='Safe Report Data', compute='_compute_safe_report_data', store=False)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        """Validate date range for enhanced wizard"""
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_('Date From cannot be later than Date To.'))

                date_diff = (record.date_to - record.date_from).days
                if date_diff > MAX_DATE_RANGE_DAYS:
                    raise ValidationError(
                        _('Date range cannot exceed %d days. Current range: %d days.')
                        % (MAX_DATE_RANGE_DAYS, date_diff)
                    )

    @api.constrains('carbon_threshold', 'compliance_threshold', 'social_impact_threshold')
    def _check_thresholds(self):
        """Validate threshold values"""
        for record in self:
            if record.carbon_threshold < 0:
                raise ValidationError(_('Carbon threshold must be non-negative.'))
            if not (0 <= record.compliance_threshold <= 100):
                raise ValidationError(_('Compliance threshold must be between 0 and 100.'))
            if not (0 <= record.social_impact_threshold <= 10):
                raise ValidationError(_('Social impact threshold must be between 0 and 10.'))

    @api.constrains('custom_metrics', 'custom_charts')
    def _check_json_fields(self):
        """Validate JSON field formats"""
        for record in self:
            if record.custom_metrics:
                try:
                    json.loads(record.custom_metrics)
                except (json.JSONDecodeError, TypeError):
                    raise ValidationError(_('Custom Metrics must be valid JSON format.'))

            if record.custom_charts:
                try:
                    json.loads(record.custom_charts)
                except (json.JSONDecodeError, TypeError):
                    raise ValidationError(_('Custom Charts must be valid JSON format.'))

    @api.model
    def create(self, vals):
        """Ensure report_data is always initialized as a dictionary and set default values"""
        try:
            # Ensure report_data is always a dictionary
            if 'report_data' not in vals or vals['report_data'] is None:
                vals['report_data'] = {}
            
            # Set default values if not provided
            if 'report_name' not in vals or not vals['report_name']:
                vals['report_name'] = 'Enhanced ESG Report'
            if 'report_type' not in vals:
                vals['report_type'] = 'sustainability'
            if 'date_from' not in vals:
                vals['date_from'] = fields.Date.today()
            if 'date_to' not in vals:
                vals['date_to'] = fields.Date.today()
            if 'company_name' not in vals or not vals['company_name']:
                vals['company_name'] = 'YourCompany'
            if 'output_format' not in vals:
                vals['output_format'] = 'pdf'
            
            return super().create(vals)
        except Exception as e:
            _logger.error(f"Error creating ESG wizard record: {str(e)}")
            raise

    def _get_report_data(self):
        """Ensure report_data is always a dictionary"""
        try:
            if not hasattr(self, 'report_data'):
                return {}
            if self.report_data is None:
                return {}
            if not isinstance(self.report_data, dict):
                return {}
            return self.report_data
        except Exception as e:
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in _get_report_data: {str(e)}")
            return {}

    def _get_report_values(self, docids, data=None):
        """Get report values for template rendering with enhanced error handling"""
        try:
            # Filter out None values from docids
            valid_docids = [docid for docid in docids if docid is not None]
            
            if not valid_docids:
                _logger.warning("No valid docids provided, creating fallback doc")
                fallback_doc = self.create({
                    'report_name': 'ESG Report',
                    'report_type': 'sustainability',
                    'date_from': fields.Date.today(),
                    'date_to': fields.Date.today(),
                    'company_name': 'YourCompany',
                    'output_format': 'pdf',
                    'report_data': {}
                })
                return {
                    'doc_ids': [fallback_doc.id],
                    'doc_model': self._name,
                    'docs': fallback_doc,
                    'data': data,
                }
            
            docs = self.browse(valid_docids)
            
            # Filter out None or invalid docs
            valid_docs = []
            for doc in docs:
                if doc and hasattr(doc, 'id') and doc.id and doc.id is not None:
                    # Ensure each doc has safe access to its data
                    if hasattr(doc, '_compute_safe_report_data_manual'):
                        try:
                            doc.safe_report_data = doc._compute_safe_report_data_manual()
                        except Exception as e:
                            _logger.error(f"Error computing safe report data for doc {doc.id}: {str(e)}")
                            doc.safe_report_data = {}
                    valid_docs.append(doc)
            
            # If no valid docs, create a fallback doc
            if not valid_docs:
                _logger.warning("No valid docs found, creating fallback doc")
                fallback_doc = self.create({
                    'report_name': 'ESG Report',
                    'report_type': 'sustainability',
                    'date_from': fields.Date.today(),
                    'date_to': fields.Date.today(),
                    'company_name': 'YourCompany',
                    'output_format': 'pdf',
                    'report_data': {}
                })
                valid_docs = [fallback_doc]
            
            return {
                'doc_ids': [doc.id for doc in valid_docs],
                'doc_model': self._name,
                'docs': valid_docs,
                'data': data,
            }
        except Exception as e:
            _logger.error(f"Error in _get_report_values: {str(e)}")
            # Return safe fallback values
            try:
                fallback_doc = self.create({
                    'report_name': 'ESG Report',
                    'report_type': 'sustainability',
                    'date_from': fields.Date.today(),
                    'date_to': fields.Date.today(),
                    'company_name': 'YourCompany',
                    'output_format': 'pdf',
                    'report_data': {}
                })
                return {
                    'doc_ids': [fallback_doc.id],
                    'doc_model': self._name,
                    'docs': [fallback_doc],
                    'data': data,
                }
            except Exception as fallback_error:
                _logger.error(f"Error creating fallback doc: {str(fallback_error)}")
                return {
                    'doc_ids': docids,
                    'doc_model': self._name,
                    'docs': [],
                    'data': data,
                }

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Update default options based on report type"""
        if self.report_type == 'sustainability':
            self.include_section_environmental = True
            self.include_section_social = True
            self.include_section_governance = True
            self.include_section_analytics = True
        elif self.report_type == 'compliance':
            self.include_section_governance = True
            self.include_thresholds = True
        elif self.report_type == 'risk_assessment':
            self.include_risk_analysis = True
            self.include_advanced_analytics = True
        elif self.report_type == 'performance_analytics':
            self.include_advanced_analytics = True
            self.include_predictive_analysis = True
            self.include_correlation_analysis = True
        elif self.report_type == 'trend_analysis':
            self.include_trends = True
            self.include_forecasting = True
        elif self.report_type == 'benchmarking':
            self.include_benchmarks = True
            self.include_section_analytics = True

    @api.onchange('comparison_period')
    def _onchange_comparison_period(self):
        """Handle comparison period changes"""
        if self.comparison_period == 'custom':
            if self.date_from and self.date_to:
                period_days = (self.date_to - self.date_from).days
                self.custom_comparison_from = self.date_from - timedelta(days=period_days)
                self.custom_comparison_to = self.date_from - timedelta(days=1)

    def action_generate_enhanced_esg_report(self):
        """Generate enhanced ESG report based on selected criteria with improved error handling"""
        try:
            # Ensure the record is properly saved and accessible
            if not self.id:
                self = self.create(self.read()[0])
            
            # Ensure we have a valid record
            if not self or not hasattr(self, 'id') or not self.id:
                raise UserError(_('Failed to create a valid ESG report wizard record.'))
            
            # Input validation
            if not self.report_name or not self.report_name.strip():
                raise UserError(_('Report name is required.'))

            if not self.date_from or not self.date_to:
                raise UserError(_('Both date from and date to are required.'))

            if self.date_from > self.date_to:
                raise UserError(_('Date From cannot be later than Date To.'))

            # Validate custom metrics JSON if provided
            if self.custom_metrics:
                try:
                    json.loads(self.custom_metrics)
                except json.JSONDecodeError:
                    raise ValidationError(_('Invalid JSON format in Custom Metrics field.'))

            _logger.info(f"Starting ESG report generation: {self.report_name} ({self.report_type})")

            # Get assets based on filters - start with less restrictive domain
            domain = self._build_asset_domain()
            assets = self.env['facilities.asset'].search(domain)

            # Try fallback strategies if no assets found
            if not assets:
                assets = self._get_fallback_assets(domain)

            _logger.info(f"Found {len(assets)} assets for ESG report")

            # Generate comprehensive report data
            report_data = self._prepare_enhanced_report_data(assets)

            # Serialize and store report data
            serialized_data = self._serialize_report_data(report_data)
            if serialized_data is None or not isinstance(serialized_data, dict):
                serialized_data = self._get_default_report_data()

            self.report_data = serialized_data
            self.invalidate_recordset(['report_data'])

            _logger.info(f"ESG report data generated successfully with {len(report_data.keys())} sections")

            # Return report action based on output format
            return self._get_report_action()

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except UserError:
            # Re-raise user errors as-is
            raise
        except Exception as e:
            # Log unexpected errors and convert to user-friendly message
            _logger.error(f"Unexpected error generating ESG report: {str(e)}", exc_info=True)
            raise UserError(_('Failed to generate ESG report. Please check the configuration and try again. Error: %s') % str(e))

    def _build_asset_domain(self):
        """Build domain for asset filtering"""
        domain = []

        # Only add date filters if dates are provided and reasonable
        if self.date_from and self.date_to and self.date_from <= self.date_to:
            domain.extend([
                ('purchase_date', '>=', self.date_from),
                ('purchase_date', '<=', self.date_to)
            ])

        if self.asset_type != 'all':
            domain.append(('category_id.category_type', '=', self.asset_type))

        if self.include_compliance_only:
            domain.append(('esg_compliance', '=', True))

        return domain

    def _get_fallback_assets(self, original_domain):
        """Get assets using fallback strategies when primary search fails"""
        # Try without date filters
        if original_domain:
            fallback_domain = []
            if self.asset_type != 'all':
                fallback_domain.append(('category_id.category_type', '=', self.asset_type))
            if self.include_compliance_only:
                fallback_domain.append(('esg_compliance', '=', True))

            if fallback_domain:
                assets = self.env['facilities.asset'].search(fallback_domain)
                if assets:
                    _logger.warning("Using fallback domain (without date filters) for asset search")
                    return assets

            # If still no assets, get all assets as last resort
            assets = self.env['facilities.asset'].search([])
            if assets:
                _logger.warning("Using all assets as fallback for ESG report generation")

            return assets

        return self.env['facilities.asset']

    def _get_report_action(self):
        """Get appropriate report action based on output format"""
        try:
            # Ensure the record is properly saved
            if not self.id:
                self = self.create(self.read()[0])
            
            # Ensure we have a valid record
            if not self or not hasattr(self, 'id') or not self.id:
                raise UserError(_('Failed to create a valid ESG report wizard record.'))
            
            # Ensure report data is available
            if not self.report_data or not isinstance(self.report_data, dict):
                # Generate report data if not available
                domain = self._build_asset_domain()
                assets = self.env['facilities.asset'].search(domain)
                
                if not assets:
                    assets = self._get_fallback_assets(domain)
                
                report_data = self._prepare_enhanced_report_data(assets)
                serialized_data = self._serialize_report_data(report_data)
                
                if serialized_data and isinstance(serialized_data, dict):
                    self.report_data = serialized_data
                    self.invalidate_recordset(['report_data'])
            
            if self.output_format == 'pdf':
                return self.env.ref('esg_reporting.action_enhanced_esg_report_pdf').report_action(self)
            elif self.output_format == 'excel':
                return self._generate_excel_report(self.report_data)
            elif self.output_format == 'html':
                return self._generate_html_report(self.report_data)
            elif self.output_format == 'json':
                return self._generate_json_report(self.report_data)
            elif self.output_format == 'csv':
                return self._generate_csv_report(self.report_data)
            else:
                raise UserError(_('Unsupported output format: %s') % self.output_format)
        except Exception as e:
            _logger.error(f"Error in _get_report_action: {str(e)}")
            raise UserError(_('Failed to generate report action. Please try again.'))

    def _prepare_enhanced_report_data(self, assets):
        """Prepare comprehensive report data with advanced analytics"""
        # Handle case when no assets are found
        if not assets:
            return {
                'report_info': {
                    'name': self.report_name,
                    'type': self.report_type,
                    'date_from': self.date_from.isoformat() if self.date_from else None,
                    'date_to': self.date_to.isoformat() if self.date_to else None,
                    'company': self.company_name,
                    'generated_at': fields.Datetime.now().isoformat(),
                    'total_assets': 0,
                    'granularity': self.granularity,
                    'theme': self.report_theme,
                    'note': 'No assets found matching the specified criteria. Please check your filters or add assets to the system.'
                },
                'environmental_metrics': {},
                'social_metrics': {},
                'governance_metrics': {},
                'analytics': {},
                'trends': {},
                'benchmarks': {},
                'risk_analysis': {},
                'predictions': {},
                'recommendations': [
                    {'category': 'data', 'recommendation': 'Add assets to the system to generate meaningful ESG reports'},
                    {'category': 'filters', 'recommendation': 'Try adjusting the date range or asset type filters'},
                    {'category': 'setup', 'recommendation': 'Ensure ESG compliance data is filled in for existing assets'}
                ],
                'thresholds': {},
                'custom_metrics': {},
                'comparison_data': {}
            }

        report_data = {
            'report_info': {
                'name': self.report_name,
                'type': self.report_type,
                'date_from': self.date_from.isoformat() if self.date_from else None,
                'date_to': self.date_to.isoformat() if self.date_to else None,
                'company': self.company_name,
                'generated_at': fields.Datetime.now().isoformat(),
                'total_assets': len(assets),
                'granularity': self.granularity,
                'theme': self.report_theme
            },
            'environmental_metrics': self._calculate_enhanced_environmental_metrics(
                assets) if self.include_section_environmental else {},
            'social_metrics': self._calculate_enhanced_social_metrics(assets) if self.include_section_social else {},
            'governance_metrics': self._calculate_enhanced_governance_metrics(
                assets) if self.include_section_governance else {},
            'analytics': self._calculate_enhanced_analytics(assets) if self.include_section_analytics else {},
            'trends': self._calculate_enhanced_trends(assets) if self.include_trends else {},
            'benchmarks': self._calculate_enhanced_benchmarks(assets) if self.include_benchmarks else {},
            'risk_analysis': self._calculate_enhanced_risk_analysis(assets) if self.include_risk_analysis else {},
            'predictions': self._calculate_enhanced_predictions(assets) if self.include_predictive_analysis else {},
            'recommendations': self._generate_enhanced_recommendations(
                assets) if self.include_section_recommendations else [],
            'thresholds': self._check_enhanced_thresholds(assets) if self.include_thresholds else {},
            'custom_metrics': json.loads(self.custom_metrics) if self.custom_metrics else {},
            'comparison_data': self._get_enhanced_comparison_data(assets) if self.comparison_period != 'none' else {}
        }

        return report_data

    def _serialize_report_data(self, data):
        """Recursively serialize data to ensure JSON compatibility"""
        if data is None:
            return {}
        elif isinstance(data, dict):
            return {key: self._serialize_report_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_report_data(item) for item in data]
        elif isinstance(data, (fields.Date, fields.Datetime)):
            return data.isoformat() if data else None
        elif hasattr(data, 'date') and callable(getattr(data, 'date', None)):
            # Handle date-like objects
            return data.isoformat() if data else None
        elif hasattr(data, 'isoformat') and callable(getattr(data, 'isoformat', None)):
            # Handle datetime-like objects
            return data.isoformat() if data else None
        elif hasattr(data, 'strftime') and callable(getattr(data, 'strftime', None)):
            # Handle date-like objects with strftime method
            return data.strftime('%Y-%m-%d') if data else None
        else:
            return data

    # Implementation of all calculation methods...
    # (Include all the calculation methods from the previous implementation)

    def _calculate_enhanced_environmental_metrics(self, assets):
        """Calculate enhanced environmental metrics with error handling"""
        try:
            metrics = {
                'total_carbon_footprint': sum(
                    getattr(asset, 'carbon_footprint', 0) or 0 for asset in assets
                ) if assets else 0,
                'energy_efficiency_score': self._calculate_energy_efficiency(assets),
                'renewable_energy_usage': self._calculate_renewable_energy(assets),
                'waste_management_score': self._calculate_waste_management(assets),
                'water_consumption': self._calculate_water_consumption(assets),
                'biodiversity_impact': self._calculate_biodiversity_impact(assets)
            }

            # Validate metric values
            for key, value in metrics.items():
                if value is None or (isinstance(value, str) and not value.strip()):
                    metrics[key] = 0
                elif not isinstance(value, (int, float)):
                    _logger.warning(f"Invalid value for {key}: {value}, setting to 0")
                    metrics[key] = 0

            return metrics
        except Exception as e:
            _logger.error(f"Error calculating environmental metrics: {str(e)}")
            return {
                'total_carbon_footprint': 0,
                'energy_efficiency_score': 0,
                'renewable_energy_usage': 0,
                'waste_management_score': 0,
                'water_consumption': 0,
                'biodiversity_impact': 0
            }

    def _calculate_enhanced_social_metrics(self, assets):
        """Calculate enhanced social metrics with error handling"""
        try:
            return {
                'community_impact_score': self._calculate_community_impact(assets),
                'employee_satisfaction': self._calculate_employee_satisfaction(assets),
                'diversity_index': self._calculate_diversity_index(assets),
                'health_safety_score': self._calculate_health_safety(assets),
                'training_hours': self._calculate_training_hours(assets),
                'local_procurement': self._calculate_local_procurement(assets)
            }
        except Exception as e:
            _logger.error(f"Error calculating social metrics: {str(e)}")
            return {
                'community_impact_score': 0,
                'employee_satisfaction': 0,
                'diversity_index': 0,
                'health_safety_score': 0,
                'training_hours': 0,
                'local_procurement': 0
            }

    def _calculate_enhanced_governance_metrics(self, assets):
        """Calculate enhanced governance metrics"""
        return {
            'compliance_rate': self._calculate_compliance_rate(assets),
            'risk_management_score': self._calculate_risk_management(assets),
            'transparency_index': self._calculate_transparency_index(assets),
            'board_diversity': self._calculate_board_diversity(assets),
            'ethics_score': self._calculate_ethics_score(assets),
            'stakeholder_engagement': self._calculate_stakeholder_engagement(assets)
        }

    def _calculate_enhanced_analytics(self, assets):
        """Calculate enhanced analytics"""
        return {
            'performance_trends': self._calculate_performance_trends(assets),
            'correlation_analysis': self._calculate_correlation_analysis(assets),
            'predictive_insights': self._calculate_predictive_insights(assets),
            'anomaly_detection': self._calculate_anomaly_detection(assets),
            'benchmark_comparison': self._calculate_benchmark_comparison(assets)
        }

    def _calculate_enhanced_trends(self, assets):
        """Calculate enhanced trends"""
        return {
            'environmental_trends': self._calculate_environmental_trends(assets),
            'social_trends': self._calculate_social_trends(assets),
            'governance_trends': self._calculate_governance_trends(assets),
            'performance_trends': self._calculate_performance_trends(assets)
        }

    def _calculate_enhanced_benchmarks(self, assets):
        """Calculate enhanced benchmarks"""
        return {
            'industry_benchmarks': self._get_industry_benchmarks(),
            'peer_comparison': self._calculate_peer_comparison(assets),
            'best_practices': self._get_best_practices(),
            'regulatory_standards': self._get_regulatory_standards()
        }

    def _calculate_enhanced_risk_analysis(self, assets):
        """Calculate enhanced risk analysis"""
        return {
            'environmental_risks': self._assess_environmental_risks(assets),
            'social_risks': self._assess_social_risks(assets),
            'governance_risks': self._assess_governance_risks(assets),
            'operational_risks': self._assess_operational_risks(assets),
            'reputation_risks': self._assess_reputation_risks(assets)
        }

    def _calculate_enhanced_predictions(self, assets):
        """Calculate enhanced predictions"""
        return {
            'carbon_footprint_forecast': self._forecast_carbon_footprint(assets),
            'performance_forecast': self._forecast_performance(assets),
            'risk_forecast': self._forecast_risks(assets),
            'compliance_forecast': self._forecast_compliance(assets)
        }

    def _generate_enhanced_recommendations(self, assets):
        """Generate enhanced recommendations"""
        recommendations = []

        # Environmental recommendations
        if self.include_section_environmental:
            recommendations.extend(self._generate_environmental_recommendations(assets))

        # Social recommendations
        if self.include_section_social:
            recommendations.extend(self._generate_social_recommendations(assets))

        # Governance recommendations
        if self.include_section_governance:
            recommendations.extend(self._generate_governance_recommendations(assets))

        return recommendations

    def _check_enhanced_thresholds(self, assets):
        """Check enhanced thresholds"""
        return {
            'carbon_threshold_exceeded': self._check_carbon_threshold(assets),
            'compliance_threshold_exceeded': self._check_compliance_threshold(assets),
            'social_impact_threshold_exceeded': self._check_social_impact_threshold(assets)
        }

    def _get_enhanced_comparison_data(self, assets):
        """Get enhanced comparison data"""
        if self.comparison_period == 'previous_period':
            return self._get_previous_period_data(assets)
        elif self.comparison_period == 'same_period_last_year':
            return self._get_same_period_last_year_data(assets)
        elif self.comparison_period == 'custom':
            return self._get_custom_period_data(assets)
        return {}

    # Helper methods for calculations
    def _calculate_energy_efficiency(self, assets):
        return 85.0  # Placeholder

    def _calculate_renewable_energy(self, assets):
        return 30.0  # Placeholder

    def _calculate_waste_management(self, assets):
        return 92.0  # Placeholder

    def _calculate_water_consumption(self, assets):
        return 1500.0  # Placeholder

    def _calculate_biodiversity_impact(self, assets):
        return 7.5  # Placeholder

    def _calculate_community_impact(self, assets):
        return 8.2  # Placeholder

    def _calculate_employee_satisfaction(self, assets):
        return 7.8  # Placeholder

    def _calculate_diversity_index(self, assets):
        return 0.75  # Placeholder

    def _calculate_health_safety(self, assets):
        return 9.1  # Placeholder

    def _calculate_training_hours(self, assets):
        return 120.0  # Placeholder

    def _calculate_local_procurement(self, assets):
        return 65.0  # Placeholder

    def _calculate_compliance_rate(self, assets):
        return 94.0  # Placeholder

    def _calculate_risk_management(self, assets):
        return 8.5  # Placeholder

    def _calculate_transparency_index(self, assets):
        return 8.7  # Placeholder

    def _calculate_board_diversity(self, assets):
        return 0.68  # Placeholder

    def _calculate_ethics_score(self, assets):
        return 9.2  # Placeholder

    def _calculate_stakeholder_engagement(self, assets):
        return 8.9  # Placeholder

    def _calculate_performance_trends(self, assets):
        return {'trend': 'improving', 'rate': 5.2}  # Placeholder

    def _calculate_correlation_analysis(self, assets):
        return {'correlation': 0.78, 'significance': 'high'}  # Placeholder

    def _calculate_predictive_insights(self, assets):
        return {'prediction': 'positive', 'confidence': 0.85}  # Placeholder

    def _calculate_anomaly_detection(self, assets):
        return {'anomalies': 2, 'severity': 'low'}  # Placeholder

    def _calculate_benchmark_comparison(self, assets):
        return {'industry_avg': 7.5, 'company_score': 8.2}  # Placeholder

    def _calculate_environmental_trends(self, assets):
        return {'direction': 'improving', 'rate': 3.1}  # Placeholder

    def _calculate_social_trends(self, assets):
        return {'direction': 'stable', 'rate': 1.2}  # Placeholder

    def _calculate_governance_trends(self, assets):
        return {'direction': 'improving', 'rate': 2.8}  # Placeholder

    def _get_industry_benchmarks(self):
        return {'environmental': 7.2, 'social': 7.8, 'governance': 8.1}  # Placeholder

    def _calculate_peer_comparison(self, assets):
        return {'rank': 15, 'total_peers': 50}  # Placeholder

    def _get_best_practices(self):
        return ['energy_efficiency', 'waste_reduction', 'community_engagement']  # Placeholder

    def _get_regulatory_standards(self):
        return {'compliance_rate': 96.5, 'standards_met': 12}  # Placeholder

    def _assess_environmental_risks(self, assets):
        return {'risk_level': 'low', 'mitigation_required': False}  # Placeholder

    def _assess_social_risks(self, assets):
        return {'risk_level': 'medium', 'mitigation_required': True}  # Placeholder

    def _assess_governance_risks(self, assets):
        return {'risk_level': 'low', 'mitigation_required': False}  # Placeholder

    def _assess_operational_risks(self, assets):
        return {'risk_level': 'medium', 'mitigation_required': True}  # Placeholder

    def _assess_reputation_risks(self, assets):
        return {'risk_level': 'low', 'mitigation_required': False}  # Placeholder

    def _forecast_carbon_footprint(self, assets):
        return {'forecast': 1200.0, 'confidence': 0.85}  # Placeholder

    def _forecast_performance(self, assets):
        return {'forecast': 8.5, 'confidence': 0.90}  # Placeholder

    def _forecast_risks(self, assets):
        return {'forecast': 'stable', 'confidence': 0.80}  # Placeholder

    def _forecast_compliance(self, assets):
        return {'forecast': 95.0, 'confidence': 0.95}  # Placeholder

    def _generate_environmental_recommendations(self, assets):
        return [
            {'category': 'energy', 'recommendation': 'Implement LED lighting upgrade'},
            {'category': 'waste', 'recommendation': 'Increase recycling program participation'}
        ]

    def _generate_social_recommendations(self, assets):
        return [
            {'category': 'diversity', 'recommendation': 'Expand diversity training programs'},
            {'category': 'community', 'recommendation': 'Increase local community partnerships'}
        ]

    def _generate_governance_recommendations(self, assets):
        return [
            {'category': 'compliance', 'recommendation': 'Strengthen internal audit procedures'},
            {'category': 'transparency', 'recommendation': 'Enhance stakeholder communication'}
        ]

    def _check_carbon_threshold(self, assets):
        total_carbon = sum(asset.carbon_footprint or 0 for asset in assets)
        return total_carbon > self.carbon_threshold

    def _check_compliance_threshold(self, assets):
        compliance_rate = self._calculate_compliance_rate(assets)
        return compliance_rate < self.compliance_threshold

    def _check_social_impact_threshold(self, assets):
        social_score = self._calculate_community_impact(assets)
        return social_score < self.social_impact_threshold

    def _get_previous_period_data(self, assets):
        return {'comparison_period': 'previous', 'data': {}}  # Placeholder

    def _get_same_period_last_year_data(self, assets):
        return {'comparison_period': 'last_year', 'data': {}}  # Placeholder

    def _get_custom_period_data(self, assets):
        return {'comparison_period': 'custom', 'data': {}}  # Placeholder

    def _generate_excel_report(self, report_data):
        """Generate Excel report"""
        # Placeholder implementation
        return {
            'type': 'ir.actions.act_url',
            'url': '/esg_reporting/download_excel',
            'target': 'self',
        }

    def _generate_html_report(self, report_data):
        """Generate HTML report"""
        # Placeholder implementation
        return {
            'type': 'ir.actions.act_url',
            'url': '/esg_reporting/download_html',
            'target': 'self',
        }

    def _generate_json_report(self, report_data):
        """Generate JSON report"""
        # Placeholder implementation
        return {
            'type': 'ir.actions.act_url',
            'url': '/esg_reporting/download_json',
            'target': 'self',
        }

    def _generate_csv_report(self, report_data):
        """Generate CSV report"""
        # Placeholder implementation
        return {
            'type': 'ir.actions.act_url',
            'url': '/esg_reporting/download_csv',
            'target': 'self',
        }
