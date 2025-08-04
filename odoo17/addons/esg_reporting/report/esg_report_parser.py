from odoo import api, models


class EnhancedEsgReportParser(models.AbstractModel):
    _name = 'report.esg_reporting.report_enhanced_esg_wizard'
    _description = 'Enhanced ESG Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        This method is called by the report engine to fetch the data.
        """
        wizard = self.env['enhanced.esg.wizard'].browse(docids[0])
        return {
            'doc_ids': docids,
            'doc_model': 'enhanced.esg.wizard',
            'docs': wizard,
            'report_data': wizard.report_data,
        }
