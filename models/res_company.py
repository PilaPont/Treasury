from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    treasury_journal_id = fields.Many2one(comodel_name='account.journal', string='Treasury Journal',
                                          default=lambda self: self.env.ref('treasury.account_treasury_journal',
                                                                            raise_if_not_found=False),
                                          required=True)
    outgoing_securities_account_id = fields.Many2one(comodel_name='account.account',
                                                     string='Outgoing Securities Account',
                                                     default=lambda self: self.env['account.account'].search(
                                                         [('code', '=', '3030')]),
                                                     required=True)
    sued_incoming_securities_account_id = fields.Many2one('account.account', string='Sued Incoming Securities Account',
                                                          default=lambda self: self.env['account.account'].search(
                                                              [('code', '=', '1570')]),
                                                          required=True)
    other_incomes_account = fields.Many2one(comodel_name='account.account', string='Other Incomes Account',
                                            default=lambda self: self.env['account.account'].search(
                                                [('code', '=', '6499')]),
                                            required=True
                                            )
    incoming_securities_account_id = fields.Many2one(comodel_name='account.account',
                                                     string='Incoming Securities Account',
                                                     default=lambda self: self.env['account.account'].search(
                                                         [('code', '=', '1530')]),
                                                     required=True)
    incoming_securities_in_bank_account_id = fields.Many2one(comodel_name='account.account',
                                                             string='Incoming Securities In Bank Account',
                                                             default=lambda self: self.env['account.account'].search(
                                                                 [('code', '=', '1935')]),
                                                             required=True)
