from odoo import models, fields, api

class CustomerLedgerReport(models.Model):
    _name = 'customer.ledger.report'
    _description = 'Customer Ledger Report'
    
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    date = fields.Date(string="Date")
    description = fields.Char(string="Description")
    debit = fields.Float(string="Debit")
    credit = fields.Float(string="Credit")
    balance = fields.Float(string="Balance")

    
    @api.model
    def get_ledger_data(self, customer_id):
        """
        Fetches customer transactions including opening balance, invoices, and payments.
        Enhanced to include invoice line details.
        """
        ledger_entries = []
        total_balance = 0

        partner = self.env['res.partner'].browse(customer_id)
        
        if partner.customer_rank > 0:
            account_type = 'asset_receivable'
        elif partner.supplier_rank > 0:
            account_type = 'liability_payable'
        else:
            return []

        # Fetch Opening Balance
        opening_balance = self.env['account.move.line'].search([
            ('partner_id', '=', customer_id),
            ('account_id.account_type', '=', account_type), 
            ('move_id.state', '=', 'posted')
        ], order='date asc', limit=1)

        if opening_balance:
            total_balance = opening_balance.debit - opening_balance.credit
            ledger_entries.append({
                'date': opening_balance.date,
                'description': opening_balance.move_id.name,
                'debit': opening_balance.debit,
                'credit': opening_balance.credit,
                'balance': total_balance,
                'move_type': opening_balance.move_id.move_type,
                'invoice_lines': []
            })
        
        # Fetch Invoices and Payments
        if partner.customer_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('move_id.state', '=', 'posted'), 
                ('id', '!=', opening_balance.id if opening_balance else False)
            ], order='date asc')
        elif partner.supplier_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'liability_payable'),
                ('move_id.state', '=', 'posted'), 
                ('id', '!=', opening_balance.id if opening_balance else False)
            ], order='date asc')

        for transaction in transactions:
            amount = transaction.debit - transaction.credit
            total_balance += amount
            
            # Get invoice line details if this is an invoice
            invoice_lines = []
            move = transaction.move_id
            if move.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                # Get all invoice lines (excluding the receivable/payable lines)
                for line in move.invoice_line_ids:
                    # Format taxes
                    taxes_str = ', '.join(line.tax_ids.mapped('name')) if line.tax_ids else ''
                    
                    invoice_lines.append({
                        'product_name': line.product_id.name or line.name or '',
                        'quantity': line.quantity,
                        'uom': line.product_uom_id.name if line.product_uom_id else '',
                        'unit_price': line.price_unit,
                        'taxes': taxes_str,
                        'line_amount': line.price_subtotal,
                    })
            
            ledger_entries.append({
                'date': transaction.date,
                'description': transaction.move_id.name,
                'debit': transaction.debit,
                'credit': transaction.credit,
                'balance': total_balance,
                'move_type': transaction.move_id.move_type,
                'invoice_lines': invoice_lines,
                'remaining_balance': total_balance
            })

        # Add Closing Balance Entry at the End
        if transactions:
            ledger_entries.append({
                'date': transactions[-1].date,
                'description': 'Closing Balance',
                'debit': 0,
                'credit': 0,
                'balance': total_balance,
                'move_type': False,
                'invoice_lines': []
            })

        return ledger_entries

    def action_export_pdf(self):
        """
        Triggers the QWeb PDF report for customer ledger.
        """
        self.ensure_one()
        return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(
            self.env['customer.ledger.report'].create({'customer_id': self.customer_id.id})
        )