# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    treasury_incoming_id = fields.Many2one(comodel_name='treasury.entry', string='Treasury Incoming')
    treasury_outgoing_id = fields.Many2one(comodel_name='treasury.entry', string='Treasury Outgoing')
