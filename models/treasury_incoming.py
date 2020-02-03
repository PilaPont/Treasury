# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _


class TreasuryIncoming(models.Model):
    _name = "treasury.incoming"
    _inherit = 'treasury.in_out_going'
    _description = "Treasury Incoming"

    received_date = fields.Date(string='Receive Date', required=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee', required=True)
    issued_by = fields.Char(string='Issued by')
    scan = fields.Binary(string="Scan", attachment=True, requierd=True)
    active = fields.Boolean(string='active', compute='_compute_active', store=True)
    transferred_to_id = fields.Many2one('res.partner', string='Transferred To')
    description = fields.Text(string='Description')

    due_state = fields.Selection([
        ('undue', 'Undue'),
        ('due', 'Due'),
        ('overdue', 'overdue')],
        compute='_compute_due',
        search='_search_due')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('undeposited', 'Undeposited'),
        ('in bank', 'In bank'),
        ('collected', 'Collected'),
        ('transferred', 'Transferred'),
        ('bounced', 'Bounced'),
        ('sued', 'Sued'),
        ('returned', 'Returned'),
        ('canceled', 'Canceled')],
        required=True, readonly=True,
        track_visibility='onchange',
        default='draft')

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for doc in self:
            doc.active = False if doc.state in ('collected', 'returned', 'canceled', 'transferred') else True

    @api.multi
    @api.depends('due_date')
    def _compute_due(self):
        if not self.due_date:
            self.due_state = 'undue'
        else:
            current_date = datetime.date.today()
            if self.due_date < current_date:
                self.due_state = 'overdue'
            elif self.due_date == current_date:
                self.due_state = 'due'
            else:
                self.due_state = 'undue'

    @api.onchange('consignee_id')
    def _onchange_consignee_id(self):
        self.issued_by = self.consignee_id.display_name

    @api.multi
    def _search_due(self, operator, value):
        current_date = datetime.date.today()
        if operator == '=':
            if value == 'overdue':
                return [('due_date', '<', current_date)]
            elif value == 'due':
                return [('due_date', '=', current_date)]
            elif value == 'undue':
                return [('due_date', '>', current_date)]
            else:
                return [('due_date', '=', False)]
        elif operator == '!=':
            if value == 'overdue':
                return [('due_date', '>=', current_date)]
            elif value == 'due':
                return ['|', ('due_date', '<', current_date), ('due_date', '>', current_date)]
            elif value == 'undue':
                return [('due_date', '<=', current_date)]
            else:
                return [('due_date', '=', False)]
        else:
            raise NotImplementedError

    @api.multi
    def set_confirm(self):
        self.state = 'undeposited'
        # debit_line_vals = {
        #     'name': self.name,
        #     'debit': self.amount,
        #     'credit': -self.amount,
        #     'account_id': self.account_rcv.id,
        # }
        # credit_line_vals = {
        #     'name': self.name,
        #     'debit': -self.amount,
        #     'credit': self.amount,
        #     'account_id': self.consignee_id.property_account_receivable_id,
        # }
        #
        # vals = {
        #     'journal_id': self.bank_journal_euro.id,
        #     'partner_id': self.consignee_id,
        #     'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        # }
        # return self.env['account.move'].create(vals).id

    @api.multi
    def set_in_bank(self):
        self.state = 'in bank'

    @api.multi
    def set_bounced(self):
        self.state = 'bounced'

    @api.multi
    def set_sued(self):
        self.state = 'sued'

    @api.multi
    def set_returned(self):
        self.state = 'returned'

    @api.multi
    def set_canceled(self):
        self.state = 'canceled'

# self.env['account.move.line'].create({
#                         'name': _('Automatic Balancing Line'),
#                         'move_id': self.account_opening_move_id.id,
#                         'account_id': balancing_account.id,
#                         'debit': credit_diff,
#                         'credit': debit_diff,
#                     })
