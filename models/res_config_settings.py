# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    treasury_journal_id = fields.Many2one('account.journal', string='Treasury Journal account',
                                          default=lambda self: self.env.ref('treasury.account_treasury_journal'),
                                          related='company_id.treasury_journal_id',
                                          readonly=False,
                                          required=True)
    outgoing_securities_account_id = fields.Many2one('account.account', string='Outgoing Securities Account',
                                                     default=lambda self: self.env.ref('l10n_ir.ac_id_3030'),
                                                     related='company_id.outgoing_securities_account_id',
                                                     readonly=False,
                                                     required=True)
    sued_incoming_securities_account_id = fields.Many2one('account.account', string='Sued Incoming Securities Account',
                                                          default=lambda self: self.env.ref('l10n_ir.ac_id_1570'),
                                                          related='company_id.sued_incoming_securities_account_id',
                                                          readonly=False,
                                                          required=True)
    incoming_securities_account_id = fields.Many2one('account.account', string='Incoming Securities Account',
                                                     default=lambda self: self.env.ref('l10n_ir.ac_id_1530'),
                                                     related='company_id.incoming_securities_account_id',
                                                     readonly=False,
                                                     required=True)
    incoming_securities_in_bank_account_id = fields.Many2one('account.account',
                                                             string='Incoming Securities In Bank Account',
                                                             default=lambda self: self.env.ref('l10n_ir.ac_id_1535'),
                                                             related='company_id.incoming_securities_in_bank_account_id',
                                                             readonly=False,
                                                             required=True)
