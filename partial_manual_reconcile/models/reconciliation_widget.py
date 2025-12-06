import logging
from odoo import api, models


_logger = logging.getLogger(__name__)


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    def get_counterpart_vals(self, values: list) -> dict:
        prepared_vals = dict()
        for rec in values:
            balance = rec['balance']
            debit = balance if balance > 0 else 0
            credit = -balance if balance < 0 else 0
            prepared_vals.update({rec['id']: {'debit': debit, 'credit': credit}})

            # Write partial residual amount
            acmvl = self.env['account.move.line'].browse(rec['id'])
            acmvl.partial_amount_residual = balance
        return prepared_vals

    @api.model
    def partial_process_move_lines(self, data, values):
        _logger.info('partial_process_move_lines function call')

        self.get_counterpart_vals(values[0]['counterpart_aml_dicts'])
        self.process_move_lines(data)
