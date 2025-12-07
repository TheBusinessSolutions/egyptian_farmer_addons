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
        Now includes detailed invoice line items.
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
                'is_invoice': False,
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
            
            # Check if this transaction is an invoice
            is_invoice = transaction.move_id.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
            invoice_lines = []
            
            if is_invoice:
                # Get invoice line items (excluding the receivable/payable line)
                invoice_lines = self._get_invoice_line_details(transaction.move_id)
            
            ledger_entries.append({
                'date': transaction.date,
                'description': transaction.move_id.name,
                'debit': transaction.debit,
                'credit': transaction.credit,
                'balance': total_balance,
                'is_invoice': is_invoice,
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
                'is_invoice': False,
                'invoice_lines': []
            })

        return ledger_entries

    def _get_invoice_line_details(self, invoice):
        """
        Extract detailed line items from an invoice.
        """
        line_details = []
        
        # Get invoice lines (exclude lines with account type receivable/payable)
        invoice_lines = invoice.invoice_line_ids
        
        for line in invoice_lines:
            # Calculate discount amount
            discount_amount = 0
            if line.discount:
                discount_amount = (line.price_unit * line.quantity * line.discount) / 100
            
            # Calculate tax amount
            tax_amount = 0
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(
                    line.price_unit,
                    line.currency_id,
                    line.quantity,
                    product=line.product_id,
                    partner=invoice.partner_id
                )
                tax_amount = sum(tax['amount'] for tax in taxes['taxes'])
            
            line_details.append({
                'product_name': line.product_id.name or line.name or 'N/A',
                'quantity': line.quantity,
                'uom': line.product_uom_id.name if line.product_uom_id else 'Unit',
                'unit_price': line.price_unit,
                'tax': tax_amount,
                'discount': line.discount,
                'discount_amount': discount_amount,
                'line_total': line.price_subtotal
            })
        
        return line_details

    def action_export_pdf(self):
        """
        Triggers the QWeb PDF report for customer ledger.
        """
        self.ensure_one()

        return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(
            self.env['customer.ledger.report'].create({'customer_id': self.customer_id.id})
        )
# from odoo import models, fields, api

# class CustomerLedgerReport(models.Model):
#     _name = 'customer.ledger.report'
#     _description = 'Customer Ledger Report'
    
#     customer_id = fields.Many2one('res.partner', string="Customer", required=True)

#     date = fields.Date(string="Date")
    
#     description = fields.Char(string="Description")
    
#     debit = fields.Float(string="Debit")
    
#     credit = fields.Float(string="Credit")
    
#     balance = fields.Float(string="Balance")

    
#     @api.model
#     def get_ledger_data(self, customer_id):
#         """
#         Fetches customer transactions including opening balance, invoices, and payments.
#         """
#         ledger_entries = []
#         total_balance = 0

#         partner = self.env['res.partner'].browse(customer_id)
        
#         if partner.customer_rank > 0:
#             account_type = 'asset_receivable'
#         elif partner.supplier_rank > 0:
#             account_type = 'liability_payable'
#         else:
#             return [] #if not customer or vendor, return an empty list.

#         # Fetch Opening Balance
#         opening_balance = self.env['account.move.line'].search([
#             ('partner_id', '=', customer_id),
#             ('account_id.account_type', '=', account_type), 
#             ('move_id.state', '=', 'posted')
#         ], order='date asc', limit=1)

#         if opening_balance:
#             total_balance = opening_balance.debit - opening_balance.credit
#             ledger_entries.append({
#                 'date': opening_balance.date,
#                 'description': opening_balance.move_id.name,
#                 'debit': opening_balance.debit,
#                 'credit': opening_balance.credit,
#                 'balance': total_balance
#             })
        
#         # Fetch Invoices and Payments
#         if partner.customer_rank > 0:
#             transactions = self.env['account.move.line'].search([
#                 ('partner_id', '=', customer_id),
#                 ('account_id.account_type', '=', 'asset_receivable'),
#                 ('move_id.state', '=', 'posted'), ('id', '!=', opening_balance.id)
#             ], order='date asc')
        
#         elif partner.supplier_rank > 0:
#             transactions = self.env['account.move.line'].search([
#                 ('partner_id', '=', customer_id),
#                 ('account_id.account_type', '=', 'liability_payable'),
#                 ('move_id.state', '=', 'posted'), ('id', '!=', opening_balance.id)
#             ], order='date asc')

#         for transaction in transactions:
#             amount = transaction.debit - transaction.credit
#             total_balance += amount
#             ledger_entries.append({
#                 'date': transaction.date,
#                 'description': transaction.move_id.name,
#                 'debit': transaction.debit,
#                 'credit': transaction.credit,
#                 'balance': total_balance,

#                 'remaining_balance': total_balance
#             })

#         # Add Closing Balance Entry at the End
#         if transactions:
#             ledger_entries.append({
#                 'date': transactions[-1].date,  # Use the date of the last transaction
#                 'description': 'Closing Balance',
#                 'debit': 0,  # Closing balance has no debit
#                 'credit': 0,  # Closing balance has no credit
#                 'balance': total_balance  # Final computed balance
#             })


#         return ledger_entries

#     def action_export_pdf(self):
#         """
#         Triggers the QWeb PDF report for customer ledger.
#         """
#         # return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(self)

#         self.ensure_one()

#         return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(
#             self.env['customer.ledger.report'].create({'customer_id': self.customer_id.id})
#             )
