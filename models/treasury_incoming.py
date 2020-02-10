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
    account_move_line_ids = fields.One2many('account.move.line', string='Journal items', readonly=True)
    account_move_ids = fields.One2many('account.move', string='Journal entries', compute='_compute_account_moves')

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
        for doc in self:
            if not doc.due_date:
                doc.due_state = 'undue'
            else:
                current_date = datetime.date.today()
                if doc.due_date < current_date:
                    doc.due_state = 'overdue'
                elif doc.due_date == current_date:
                    doc.due_state = 'due'
                else:
                    doc.due_state = 'undue'

    @api.multi
    @api.depends
    def _compute_account_moves(self):
        for doc in self:
            doc.account_move_ids = doc.mapped('account_move_line_ids.move_id')

    @api.onchange('consignee_id')
    def _onchange_consignee_id(self):
        self.issued_by = self.consignee_id.display_name

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
                'name': 'Receiving {} {} for {}'.format(self.security_type_id.name, self.number,
                                                        self.env.context.get('payment_description') or self.reason),
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
                'ref': 'Receiving {} {} for {}'.format(self.security_type_id.name, self.number,
                                                       self.env.context.get('payment_description') or self.reason)
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_in_bank(self):
        self.state = 'in bank'
        credit_account = self.company_id.incoming_securities_account_id.id if self.guaranty \
            else self.company_id.other_incomes_account.id

        debit_line_vals = {
            'name': 'Delivering {} {} for {}'.format(self.security_type_id.name, self.number,
                                                     self.env.context.get('payment_description') or self.reason),
            'debit': self.amount,
            'account_id': self.company_id.incoming_securities_in_bank_account_id.id,
        }
        credit_line_vals = {
            'name': self.name,
            'credit': self.amount,
            'account_id': credit_account,
        }

        vals = {
            'journal_id': self.company_id.treasury_journal_id.id,
            'partner_id': self.consignee_id.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
            'ref': 'Delivering {} {} for {}'.format(self.security_type_id.name, self.number,
                                                    self.env.context.get('payment_description') or self.reason),
        }
        return self.env['account.move'].create(vals).id

    @api.multi
    def action_bounce(self):
        self.state = 'bounced'

        debit_line_vals = {
            'name': 'Bouncing {} {} for {}'.format(self.security_type_id.name, self.number,
                                                   self.env.context.get('payment_description') or self.reason),
            'debit': self.amount,
            'account_id': self.consignee_id.property_account_receivable_id.id,
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
            'ref': 'Bouncing {} {} for {}'.format(self.security_type_id.name, self.number,
                                                  self.env.context.get('payment_description') or self.reason),
        }
        return self.env['account.move'].create(vals).id

    @api.multi
    def action_sue(self):
        self.state = 'sued'
        if not self.guaranty:
            debit_line_vals = {
                'name': 'Suing {} {} for {}'.format(self.security_type_id.name, self.number,
                                                    self.env.context.get('payment_description') or self.reason),
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
                'ref': 'Suing {} {} for {}'.format(self.security_type_id.name, self.number,
                                                   self.env.context.get('payment_description') or self.reason),
            }
            return self.env['account.move'].create(vals).id

    @api.multi
    def action_return(self):
        self.state = 'returned'
        if not self.guaranty:
            debit_line_vals = {
                'name': 'Returning {} {} for {}'.format(self.security_type_id.name, self.number,
                                                        self.env.context.get('payment_description') or self.reason),
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
                'ref': 'Returning {} {} for {}'.format(self.security_type_id.name, self.number,
                                                       self.env.context.get('payment_description') or self.reason),
            }
            return self.env['account.move'].create(vals).id
