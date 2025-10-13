from odoo import models, fields, api

class CustomerLedgerReport(models.Model):
    _name = 'customer.ledger.report'
    _description = 'Customer Ledger Report'
    _order = 'date, is_invoice_line'
    
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)

    date = fields.Date(string="Date")
    
    description = fields.Char(string="Description")
    
    debit = fields.Float(string="Debit")
    
    credit = fields.Float(string="Credit")
    
    balance = fields.Float(string="Balance")

    # Add new fields for invoice lines
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="UoM")
    unit_price = fields.Float(string="Unit Price")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    item_total = fields.Float(string="Item Total")
    is_invoice_line = fields.Boolean(string="Is Invoice Line")
    parent_move_id = fields.Many2one('account.move', string="Parent Invoice")

    @api.model
    def get_ledger_data(self, customer_id):
        """
        Fetches customer transactions including opening balance, invoices, and payments.
        """
        ledger_entries = []
        total_balance = 0

        partner = self.env['res.partner'].browse(customer_id)
        
        if partner.customer_rank > 0:
            account_type = 'asset_receivable'
        elif partner.supplier_rank > 0:
            account_type = 'liability_payable'
        else:
            return [] #if not customer or vendor, return an empty list.

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
                'balance': total_balance
            })
        
        # Fetch Invoices and Payments
        if partner.customer_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('move_id.state', '=', 'posted'), ('id', '!=', opening_balance.id)
            ], order='date asc')
        
        elif partner.supplier_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'liability_payable'),
                ('move_id.state', '=', 'posted'), ('id', '!=', opening_balance.id)
            ], order='date asc')

        for transaction in transactions:
            amount = transaction.debit - transaction.credit
            total_balance += amount
            
            entry = {
                'date': transaction.date,
                'description': transaction.move_id.name,
                'debit': transaction.debit,
                'credit': transaction.credit,
                'balance': total_balance,
                'remaining_balance': total_balance,
                'is_invoice_line': False,
                'parent_move_id': transaction.move_id.id
            }
            ledger_entries.append(entry)

            # Add invoice lines if this is an invoice
            if transaction.move_id.move_type in ['out_invoice', 'in_invoice']:
                for line in transaction.move_id.invoice_line_ids:
                    line_entry = {
                        'date': transaction.date,
                        'description': f"    • {line.product_id.name or ''}",  # Indented description
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'uom_id': line.product_uom_id.id,
                        'unit_price': line.price_unit,
                        'tax_ids': line.tax_ids.ids,
                        'item_total': line.price_subtotal,
                        'debit': 0,
                        'credit': 0,
                        'balance': total_balance,
                        'is_invoice_line': True,
                        'parent_move_id': transaction.move_id.id
                    }
                    ledger_entries.append(line_entry)

        # Add Closing Balance Entry at the End
        if transactions:
            ledger_entries.append({
                'date': transactions[-1].date,  # Use the date of the last transaction
                'description': 'Closing Balance',
                'debit': 0,  # Closing balance has no debit
                'credit': 0,  # Closing balance has no credit
                'balance': total_balance  # Final computed balance
            })


        return ledger_entries

    @api.model
    def create_ledger_entries(self, customer_id):
        """Creates actual records in the table instead of virtual ones"""
        entries = self.get_ledger_data(customer_id)
        created_entries = []
        
        for entry in entries:
            record = self.create(entry)
            created_entries.append(record.id)
            
        return created_entries

    def action_view_report(self):
        """Action to view the report"""
        self.search([]).unlink()  # Clear existing entries
        entries = self.create_ledger_entries(self.customer_id.id)
        
        return {
            'name': 'Customer Ledger',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.ledger.report',
            'view_mode': 'tree',
            'view_id': self.env.ref('customer_partner_ledger.view_customer_ledger_report_tree').id,
            'domain': [('id', 'in', entries)],
            'context': {'search_default_customer_id': self.customer_id.id}
        }

    def action_export_pdf(self):
        """Triggers the QWeb PDF report for customer ledger."""
        self.ensure_one()
        entries = self.create_ledger_entries(self.customer_id.id)
        
        return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(
            self.browse(entries)
        )
