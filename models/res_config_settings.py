from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    treasury_journal_id = fields.Many2one(comodel_name='account.journal', string='Treasury Journal',
                                          related='company_id.treasury_journal_id',
                                          readonly=False,
                                          required=True)
    outgoing_securities_account_id = fields.Many2one(comodel_name='account.account',
                                                     string='Outgoing Securities Account',
                                                     default=lambda self: self.env['account.account'].search(
                                                         [('code', '=', '3030')]),
                                                     related='company_id.outgoing_securities_account_id',
                                                     readonly=False,
                                                     required=True)
    sued_incoming_securities_account_id = fields.Many2one(comodel_name='account.account',
                                                          string='Sued Incoming Securities Account',
                                                          default=lambda self: self.env['account.account'].search(
                                                              [('code', '=', '1570')]),
                                                          related='company_id.sued_incoming_securities_account_id',
                                                          readonly=False,
                                                          required=True)
    other_incomes_account = fields.Many2one(comodel_name='account.account', string='Other Incomes Account',
                                            default=lambda self: self.env['account.account'].search(
                                                [('code', '=', '6499')]),
                                            related='company_id.other_incomes_account',
                                            readonly=False,
                                            required=True
                                            )
    incoming_securities_account_id = fields.Many2one(comodel_name='account.account',
                                                     string='Incoming Securities Account',
                                                     default=lambda self: self.env['account.account'].search(
                                                         [('code', '=', '1530')]),
                                                     related='company_id.incoming_securities_account_id',
                                                     readonly=False,
                                                     required=True)
    incoming_securities_in_bank_account_id = fields.Many2one(comodel_name='account.account',
                                                             string='Incoming Securities In Bank Account',
                                                             default=lambda self: self.env['account.account'].search(
                                                                 [('code', '=', '1535')]),
                                                             related='company_id.incoming_securities_in_bank_account_id',
                                                             readonly=False,
                                                             required=True)
