# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TreasuryIncoming(models.Model):
    _name = "treasury.incoming"
    _inherit = 'treasury.entry'
    _description = "Treasury Incoming"

    received_date = fields.Date(string='Receive Date', required=True)
    consignee_id = fields.Many2one(comodel_name='res.partner', string='Consignee', required=True)
    issued_by = fields.Char(string='Issued by', required=True)
    scan = fields.Binary(string="Scan", attachment=True, requierd=True)
    active = fields.Boolean(string='active', compute='_compute_active', store=True)
    transferred_to_id = fields.Many2one(comodel_name='res.partner', string='Transferred To')
    description = fields.Text(string='Description')
    account_move_line_ids = fields.One2many(comodel_name='account.move.line', inverse_name='treasury_incoming_id',
                                            string='Journal items', readonly=True)
    account_move_ids = fields.One2many(comodel_name='account.move', string='Journal entries',
                                       compute='_compute_account_moves')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('undeposited', 'Undeposited'),
        ('in_bank', 'In bank'),
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
    @api.depends('account_move_line_ids')
    def _compute_account_moves(self):
        for doc in self:
            doc.account_move_ids = doc.mapped('account_move_line_ids.move_id')

    @api.onchange('consignee_id')
    def _onchange_consignee_id(self):
        self.issued_by = self.consignee_id.display_name

    @api.multi
    def action_confirm(self):
        for doc in self:
            doc.state = 'undeposited'
            if not doc.guaranty:
                name_and_ref = 'Receiving {} {} for {}'.format(doc.security_type_id.name, doc.number,
                                                               doc.env.context.get('payment_description') or doc.reason)
                debit_line_vals = {
                    'name': name_and_ref,
                    'debit': doc.amount,
                    'account_id': doc.company_id.incoming_securities_account_id.id,
                }
                credit_line_vals = {
                    'name': name_and_ref,
                    'credit': doc.amount,
                    'account_id': doc.consignee_id.property_account_receivable_id.id,
                }

                vals = {
                    'journal_id': doc.company_id.treasury_journal_id.id,
                    'partner_id': doc.consignee_id.id,
                    'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                    'ref': name_and_ref
                }
                new_move = doc.env['account.move'].create(vals)
                doc.account_move_line_ids += new_move.line_ids

    @api.multi
    def action_in_bank(self):
        for doc in self:
            doc.state = 'in_bank'
            credit_account = doc.company_id.incoming_securities_account_id.id if doc.guaranty \
                else doc.company_id.other_incomes_account.id
            name_and_ref = 'Delivering {} {} for {}'.format(doc.security_type_id.name, doc.number,
                                                            doc.env.context.get('payment_description') or doc.reason)
            debit_line_vals = {
                'name': name_and_ref,
                'debit': doc.amount,
                'account_id': doc.company_id.incoming_securities_in_bank_account_id.id,
            }
            credit_line_vals = {
                'name': name_and_ref,
                'credit': doc.amount,
                'account_id': credit_account,
            }

            vals = {
                'journal_id': doc.company_id.treasury_journal_id.id,
                'partner_id': doc.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': name_and_ref,
            }
            new_move = doc.env['account.move'].create(vals)
            doc.account_move_line_ids += new_move.line_ids

    @api.multi
    def action_bounce(self):
        for doc in self:
            self.state = 'bounced'
            name_and_ref = 'Bouncing {} {} for {}'.format(doc.security_type_id.name, doc.number,
                                                          doc.env.context.get('payment_description') or doc.reason)
            debit_line_vals = {
                'name': name_and_ref,
                'debit': doc.amount,
                'account_id': doc.consignee_id.property_account_receivable_id.id,
            }
            credit_line_vals = {
                'name': name_and_ref,
                'credit': doc.amount,
                'account_id': doc.company_id.incoming_securities_in_bank_account_id.id,
            }

            vals = {
                'journal_id': doc.company_id.treasury_journal_id.id,
                'partner_id': doc.consignee_id.id,
                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                'ref': name_and_ref,
            }
            new_move = doc.env['account.move'].create(vals)
            doc.account_move_line_ids += new_move.line_ids

    @api.multi
    def action_sue(self):
        for doc in self:
            doc.state = 'sued'
            if not doc.guaranty:
                name_and_ref = 'Suing {} {} for {}'.format(doc.security_type_id.name, doc.number,
                                                           doc.env.context.get('payment_description') or doc.reason)
                debit_line_vals = {
                    'name': name_and_ref,
                    'debit': doc.amount,
                    'account_id': doc.company_id.incoming_securities_account_id.id,
                }
                credit_line_vals = {
                    'name': name_and_ref,
                    'credit': doc.amount,
                    'account_id': doc.company_id.sued_incoming_securities_account_id.id,
                }

                vals = {
                    'journal_id': doc.company_id.treasury_journal_id.id,
                    'partner_id': doc.consignee_id.id,
                    'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                    'ref': name_and_ref,
                }
                new_move = doc.env['account.move'].create(vals)
                doc.account_move_line_ids += new_move.line_ids

    @api.multi
    def action_return(self):
        for doc in self:
            doc.state = 'returned'
            if not doc.guaranty:
                name_and_ref = 'Returning {} {} for {}'.format(doc.security_type_id.name, doc.number,
                                                               doc.env.context.get('payment_description') or doc.reason)
                debit_line_vals = {
                    'name': name_and_ref,
                    'debit': doc.amount,
                    'account_id': doc.consignee_id.property_account_receivable_id.id,
                }
                credit_line_vals = {
                    'name': name_and_ref,
                    'credit': doc.amount,
                    'account_id': doc.company_id.incoming_securities_account_id.id,
                }

                vals = {
                    'journal_id': doc.company_id.treasury_journal_id.id,
                    'partner_id': doc.consignee_id.id,
                    'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
                    'ref': name_and_ref,
                }
                new_move = doc.env['account.move'].create(vals)
                doc.account_move_line_ids += new_move.line_ids
