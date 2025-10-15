from odoo import models, fields, api

class CustomerLedgerWizard(models.TransientModel):
    _name = 'customer.ledger.wizard'
    _description = 'Customer Ledger Wizard'

    customer_id = fields.Many2one('res.partner', string="Customer", required=True)

    def action_generate_ledger(self):
        """
        Triggers the QWeb PDF report for the customer ledger.
        """
        self.ensure_one()

        return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(
            self.env['customer.ledger.report'].create({'customer_id': self.customer_id.id})
        )

    def action_preview_report(self):
        self.ensure_one()

        # Clear previous records for this customer (Optional)
        self.env['customer.ledger.report'].search([('customer_id', '=', self.customer_id.id)]).unlink()

        # Get ledger data
        ledger_data = self.env['customer.ledger.report'].get_ledger_data(self.customer_id.id)

        # Create records with invoice lines
        for entry in ledger_data:
            # Create main ledger record
            ledger_record = self.env['customer.ledger.report'].create({
                'customer_id': self.customer_id.id,
                'date': entry.get('date'),
                'description': entry.get('description'),
                'debit': entry.get('debit'),
                'credit': entry.get('credit'),
                'balance': entry.get('balance'),
            })
            
            # Create invoice line records if they exist
            if entry.get('invoice_lines'):
                for line in entry['invoice_lines']:
                    self.env['customer.ledger.line'].create({
                        'ledger_id': ledger_record.id,
                        'product_name': line.get('product_name'),
                        'quantity': line.get('quantity'),
                        'uom': line.get('uom'),
                        'unit_price': line.get('unit_price'),
                        'taxes': line.get('taxes'),
                        'line_amount': line.get('line_amount'),
                    })

        # Return an action to open the tree view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Ledger',
            'view_mode': 'tree,form',
            'res_model': 'customer.ledger.report',
            'views': [
                (self.env.ref('customer_partner_ledger.view_customer_ledger_report_tree').id, 'tree'),
                (self.env.ref('customer_partner_ledger.view_customer_ledger_report_form').id, 'form')
            ],
            'domain': [('customer_id', '=', self.customer_id.id)],
            'target': 'current',
        }