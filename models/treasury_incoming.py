# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _


class TreasuryIncoming(models.Model):
    _name = "treasury.incoming"
    _inherit = 'treasury.in_out_going'
    _description = "Treasury Incoming"

    received_date = fields.Date(string='Receive Date', required=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee', required=True)
    issued_by = fields.Char(string='Issued by', required=True)
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
        ('returned', 'Returned'), ],
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
    def action_confirm(self):
        self.state = 'undeposited'
        if not self.guaranty:
            debit_line_vals = {
                'name': self.name,
                'debit': self.amount,
                'account_id': self.company_id.incoming_securities_account_id.id,
            }
            credit_line_vals = {
                'name': self.name,
                'credit': self.amount,
                'account_id': self.consignee_id.property_account_receivable_id.id,
            }

            vals = {
                'journal_id': self.company_id.treasury_journal_id.id,
                'partner_id': self.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': 'confirm security'
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_in_bank(self):
        self.state = 'in bank'
        if not self.guaranty:
            debit_line_vals = {
                'name': self.name,
                'debit': self.amount,
                'account_id': self.company_id.incoming_securities_in_bank_account_id.id,
            }
            credit_line_vals = {
                'name': self.name,
                'credit': self.amount,
                'account_id': self.company_id.incoming_securities_account_id.id,
            }

            vals = {
                'journal_id': self.company_id.treasury_journal_id.id,
                'partner_id': self.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': 'send security to bank'
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_bounce(self):
        self.state = 'bounced'
        if not self.guaranty:
            debit_line_vals = {
                'name': self.name,
                'debit': self.amount,
                'account_id': self.company_id.incoming_securities_account_id.id,
            }
            credit_line_vals = {
                'name': self.name,
                'credit': self.amount,
                'account_id': self.company_id.incoming_securities_in_bank_account_id.id,
            }

            vals = {
                'journal_id': self.company_id.treasury_journal_id.id,
                'partner_id': self.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': 'bounce security'
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_sue(self):
        self.state = 'sued'
        if not self.guaranty:
            debit_line_vals = {
                'name': self.name,
                'debit': self.amount,
                'account_id': self.company_id.incoming_securities_account_id.id,
            }
            credit_line_vals = {
                'name': self.name,
                'credit': self.amount,
                'account_id': self.company_id.sued_incoming_securities_account_id.id,
            }

            vals = {
                'journal_id': self.company_id.treasury_journal_id.id,
                'partner_id': self.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': 'sue security'
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_return(self):
        self.state = 'returned'
        if not self.guaranty:
            debit_line_vals = {
                'name': self.name,
                'debit': self.amount,
                'account_id': self.consignee_id.property_account_receivable_id.id,
            }
            credit_line_vals = {
                'name': self.name,
                'credit': self.amount,
                'account_id': self.company_id.incoming_securities_account_id.id,
            }

            vals = {
                'journal_id': self.company_id.treasury_journal_id.id,
                'partner_id': self.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': 'return security'
            }
            return self.env['account.move'].create(vals).id

