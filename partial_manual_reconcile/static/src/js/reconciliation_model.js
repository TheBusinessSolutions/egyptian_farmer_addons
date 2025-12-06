odoo.define('partial_manual_reconcile.ReconciliationModel', function (require) {
    "use strict";

    let session = require('web.session');
    let utils = require('web.utils');
    let core = require('web.core');
    let _t = core._t;
    let ReconciliationModel = require('account.ReconciliationModel');

    ReconciliationModel.ManualModel.include({
        _checkActionPayment: function () {
            return window.location.href.includes('action=manual_reconciliation_view');
        },

        validate: function (handle) {
            if (this._checkActionPayment()) {
                return this.customValidate(handle);
            }
            return this._super.apply(this, arguments);
        },

        _computeLine: function (line) {
            if (this._checkActionPayment()) {
                return this._super(line).then(function () {
                var props = _.reject(line.reconciliation_proposition, 'invalid');
                _.each(line.reconciliation_proposition, function (p) {
                    p.is_move_line = true;
                });
                line.balance.type = -1;
                if (!line.balance.amount_currency && props.length) {
                    line.balance.type = 1;
                } else if (_.any(props, function (prop) {
                        return prop.amount > 0;
                    }) &&
                    _.any(props, function (prop) {
                        return prop.amount < 0;
                    })) {
                    line.balance.type = 0;
                }
            });
            }
            return this._super.apply(this, arguments);
        },
        /**
         * Mark the account or the partner as reconciled
         *
         * @param {(string|string[])} handle
         * @returns {Promise<Array>} resolved with the handle array
         */
        customValidate: function (handle) {
            var self = this;
            var handles = [];
            if (handle) {
                handles = [handle];
            } else {
                _.each(this.lines, function (line, handle) {
                    if (!line.reconciled && !line.balance.amount && line.reconciliation_proposition.length) {
                        handles.push(handle);
                    }
                });
            }

            var process_reconciliations = [];
            var reconciled = [];

            // NEW
            var values = [];
            var handlesPromises = [];

            _.each(handles, function (handle) {
                var line = self.getLine(handle);

                // NEW
                var computeLinePromise = self._computeLine(line);

                if (line.reconciled) {
                    return;
                }
                var props = line.reconciliation_proposition;
                if (!props.length) {
                    self.valuenow++;
                    reconciled.push(handle);
                    line.reconciled = true;
                    process_reconciliations.push({
                        id: line.type === 'accounts' ? line.account_id : line.partner_id,
                        type: line.type,
                        mv_line_ids: [],
                        new_mv_line_dicts: [],
                    });
                } else {
                    var mv_line_ids = _.pluck(_.filter(props, function (prop) {
                        return !isNaN(prop.id);
                    }), 'id');
                    var new_mv_line_dicts = _.map(_.filter(props, function (prop) {
                        return isNaN(prop.id) && prop.display;
                    }), self._formatToProcessReconciliation.bind(self, line));
                    process_reconciliations.push({
                        id: null,
                        type: null,
                        mv_line_ids: mv_line_ids,
                        new_mv_line_dicts: new_mv_line_dicts
                    });
                }
                line.reconciliation_proposition = [];

                // NEW
                // TODO: leave only needed values from counterpart_aml_dicts object
                handlesPromises.push(Promise.resolve(computeLinePromise).then(function () {
                    var values_dict = {
                        "partner_id": line.st_line.partner_id,
                        "counterpart_aml_dicts": _.map(_.filter(props, function (prop) {
                            return !isNaN(prop.id) && !prop.already_paid;
                        }), self._formatToProcessReconciliation.bind(self, line)),
                        "payment_aml_ids": _.pluck(_.filter(props, function (prop) {
                            return !isNaN(prop.id) && prop.already_paid;
                        }), 'id'),
                        "new_aml_dicts": _.map(_.filter(props, function (prop) {
                            return isNaN(prop.id) && prop.display;
                        }), self._formatToProcessReconciliation.bind(self, line)),
                        "to_check": line.to_check,
                    };

                    // If the lines are not fully balanced, create an unreconciled amount.
                    // line.st_line.currency_id is never false here because its equivalent to
                    // statement_line.currency_id or statement_line.journal_id.currency_id or statement_line.journal_id.company_id.currency_id (Python-side).
                    // see: get_statement_line_for_reconciliation_widget method in account/models/account_bank_statement.py for more details
                    var currency = session.get_currency(line.st_line.currency_id);
                    var balance = line.balance.amount;
                    if (!utils.float_is_zero(balance, currency.digits[1])) {
                        var unreconciled_amount_dict = {
                            'account_id': line.st_line.open_balance_account_id,
                            'credit': balance > 0 ? balance : 0,
                            'debit': balance < 0 ? -balance : 0,
                            'name': line.st_line.name + ' : ' + _t("Open balance"),
                        };
                        values_dict['new_aml_dicts'].push(unreconciled_amount_dict);
                    }
                    values.push(values_dict);
                    line.reconciled = true;
                }));
            });

            return Promise.all(handlesPromises).then(function () {
                return self._rpc({
                    model: 'account.reconciliation.widget',
                    method: 'partial_process_move_lines',
                    args: [process_reconciliations, values],
                }).then(function () {

                    let paymentID = self.context.active_id;
                    window.location.href = '#id=' + paymentID + '&model=account.payment&view_type=form';

                    return {handles: handles}
                });
            });
        },
    })
});
