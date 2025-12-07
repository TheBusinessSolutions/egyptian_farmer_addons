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
        Now includes detailed invoice line items and transaction types.
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

        # Fetch Opening Balance (if exists)
        opening_balance = self.env['account.move.line'].search([
            ('partner_id', '=', customer_id),
            ('account_id.account_type', '=', account_type), 
            ('move_id.state', '=', 'posted')
        ], order='date asc', limit=1)

        opening_balance_id = False
        if opening_balance:
            # Only add opening balance if it's not an invoice (to avoid duplication)
            if opening_balance.move_id.move_type not in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund', 'entry']:
                total_balance = opening_balance.debit - opening_balance.credit
                ledger_entries.append({
                    'date': opening_balance.date,
                    'description': opening_balance.move_id.name,
                    'type': 'Opening Balance',
                    'debit': opening_balance.debit,
                    'credit': opening_balance.credit,
                    'balance': total_balance,
                    'is_invoice': False,
                    'invoice_lines': [],
                    'related_payments': []
                })
                opening_balance_id = opening_balance.id
        
        # Fetch ALL Invoices and Payments
        if partner.customer_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('move_id.state', '=', 'posted')
            ], order='date asc, id asc')
        
        elif partner.supplier_rank > 0:
            transactions = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id),
                ('account_id.account_type', '=', 'liability_payable'),
                ('move_id.state', '=', 'posted')
            ], order='date asc, id asc')

        # Group transactions by invoice to track payments
        invoice_entries = {}
        
        # Process each transaction
        for transaction in transactions:
            # Skip if this was already added as opening balance
            if opening_balance_id and transaction.id == opening_balance_id:
                continue
                
            amount = transaction.debit - transaction.credit
            total_balance += amount
            
            # Determine transaction type
            move_type = transaction.move_id.move_type
            transaction_type = self._get_transaction_type(move_type)
            
            # Check if this transaction is an invoice
            is_invoice = move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
            invoice_lines = []
            
            if is_invoice:
                # Get invoice line items
                invoice_lines = self._get_invoice_line_details(transaction.move_id)
            
            entry = {
                'date': transaction.date,
                'description': transaction.move_id.name,
                'type': transaction_type,
                'debit': transaction.debit,
                'credit': transaction.credit,
                'balance': total_balance,
                'is_invoice': is_invoice,
                'invoice_lines': invoice_lines,
                'move_id': transaction.move_id.id,
                'related_payments': [],
                'remaining_balance': total_balance
            }
            
            ledger_entries.append(entry)
            
            # Store invoice entries for payment matching
            if is_invoice:
                invoice_entries[transaction.move_id.id] = entry

        # Match payments to invoices
        self._link_payments_to_invoices(ledger_entries, invoice_entries)

        # Add Closing Balance Entry at the End
        if ledger_entries:
            ledger_entries.append({
                'date': ledger_entries[-1]['date'],
                'description': 'Closing Balance',
                'type': 'Closing',
                'debit': 0,
                'credit': 0,
                'balance': total_balance,
                'is_invoice': False,
                'invoice_lines': [],
                'related_payments': []
            })

        return ledger_entries

    def _get_transaction_type(self, move_type):
        """
        Determine the transaction type based on move_type.
        """
        type_mapping = {
            'out_invoice': 'Invoice',
            'in_invoice': 'Bill',
            'out_refund': 'Refund',
            'in_refund': 'Vendor Refund',
            'entry': 'Payment',
        }
        return type_mapping.get(move_type, 'Payment')

    def _link_payments_to_invoices(self, ledger_entries, invoice_entries):
        """
        Link payment entries to their related invoices.
        """
        for entry in ledger_entries:
            # Skip if not a payment
            if entry['type'] not in ['Payment', 'Journal Entry']:
                continue
            
            # Get the account move
            move = self.env['account.move'].browse(entry['move_id'])
            
            # Find reconciled invoices
            for line in move.line_ids:
                if line.account_id.account_type in ['asset_receivable', 'liability_payable']:
                    # Get reconciled items
                    reconciled_lines = line.matched_debit_ids | line.matched_credit_ids
                    
                    for reconcile in reconciled_lines:
                        # Get the other side of the reconciliation
                        other_line = reconcile.debit_move_id if reconcile.credit_move_id == line else reconcile.credit_move_id
                        
                        # Check if this is linked to an invoice in our entries
                        if other_line.move_id.id in invoice_entries:
                            payment_info = {
                                'date': entry['date'],
                                'description': entry['description'],
                                'amount': reconcile.amount,
                                'payment_type': entry['type']
                            }
                            invoice_entries[other_line.move_id.id]['related_payments'].append(payment_info)

    def _get_invoice_line_details(self, invoice):
        """
        Extract detailed line items from an invoice.
        """
        line_details = []
        
        # Get invoice lines
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