from odoo import models, fields, api


class PartnerTrialBalanceReport(models.AbstractModel):
    _name = 'report.partner_trial_balance_report.partner_trial_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        cr = self.env.cr
        query = """
                       SELECT
                           p.company_registry AS party_code,
                           p.name AS partner_name,
                           SUM(l.debit) AS debit, 
                           SUM(l.credit) AS credit,
                           SUM(l.debit) - SUM(l.credit) AS balance
                       FROM
                           account_move_line l
                       JOIN
                           account_move m ON l.move_id = m.id
                       JOIN
                           res_partner p ON l.partner_id = p.id
                       WHERE
                           l.date BETWEEN %s AND %s
                           AND m.state = 'posted'
                           AND l.company_id = %s
                       """
        params = [data['date_from'], data['date_to'], data['company']]

        if data['selection'] == 'customer':
            query += " AND p.customer_rank > 0"
        else:
            query += " AND p.supplier_rank > 0"

        if 'partner_id' in data and data['partner_id']:
            query += " AND l.partner_id = %s"
            params.append(data['partner_id'])

        query += " GROUP BY p.name, p.company_registry"
        query += " ORDER BY p.company_registry"
        cr.execute(query, params)
        results = cr.fetchall()
        report_values = []
        for row in results:
            report_values.append({
                'partner_name': row[0] + "-" + row[1] if row[0] else row[1],
                'debit': row[2],
                'credit': row[3],
                'balance': row[4]
            })
        return {
            'data': data,
            'report_values': report_values,
        }
