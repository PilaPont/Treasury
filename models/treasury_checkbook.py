from odoo import api, fields, models, _, exceptions


class TreasuryCheckbook(models.Model):
    _name = "treasury.checkbook"
    _description = "Treasury Checkbook"

    journal_id = fields.Many2one('account.journal', string='Bank Account Journal', required=True)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account',
                                      related='journal_id.bank_account_id', readonly=True)
    company_id = fields.Many2one('res.company', string='company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    check_ids = fields.One2many('treasury.outgoing', string='Check', inverse_name='checkbook_id',
                                required=True, domain=[('type', '=', 'check')])
    first_serial_no = fields.Integer(string='First Check Serial No.', required=True)
    last_serial_no = fields.Integer(string='Last Check Serial No.', compute='_compute_last_serial_no', store=True)
    series_no = fields.Integer(string='Series No.', required=True)
    remained = fields.Integer(string='# Remained', compute='_compute_remained_state', store=True)
    next_check = fields.Char(string='next check No.', compute='_compute_next')
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    active = fields.Boolean(string='active', compute='_compute_active', store=True)
    count = fields.Integer(string='Count')
    renew = fields.Boolean(string='Running Out', compute='_compute_renew', store=True)
    select_count = fields.Selection(selection=[
        ('10', '10'),
        ('20', '20'),
        ('50', '50'),
        ('custom_count', 'Custom Count')],
        string='Select Count')
    state = fields.Selection([
        ('open', 'Open'),
        ('finished', 'Finished'),
        ('done', 'Done')],
        default='open',
        compute='_compute_remained_state',
        store=True)

    @api.multi
    @api.depends('first_serial_no')
    def _compute_last_serial_no(self):
        for check_book in self:
            check_book.last_serial_no = check_book.first_serial_no + check_book.count

    @api.multi
    @api.depends('check_ids.state')
    def _compute_remained_state(self):
        for check_book in self:
            if all(check.state in ('cashed', 'canceled') for check in check_book.check_ids):
                check_book.state = 'done'
                check_book.remained = 0
            else:
                check_book.remained = len(check_book.check_ids.filtered(lambda x: x.state in ('draft', 'new')))
                check_book.state = 'open' if check_book.remained else 'finished'

    @api.multi
    def _compute_next(self):
        for check_book in self:
            check_book.next_check = self.env['treasury.outgoing'].search(
                [('state', '=', 'new'), ('type', '=', 'check')], limit=1).get_name()  # todo: Make sure it works!

    @api.multi
    @api.depends('journal_id.name', 'first_serial_no', 'count')
    def _compute_display_name(self):
        for check_book in self:
            check_book.display_name = '{} ({}_{})'.format(self.journal_id.name, self.first_serial_no,
                                                          int(self.first_serial_no) + self.count)

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for check_book in self:
            check_book.active = False if check_book.state == 'done' else True

    @api.multi
    @api.depends('remained')
    def _compute_renew(self):
        for check_book in self:
            check_book.renew = True if check_book.remained <= check_book.count / 5 else False

    @api.onchange('select_count')
    def _onchange_select_count(self):
        try:
            self.count = int(self.select_count)
        except Exception as e:
            print(e)

    @api.model
    def create(self, vals):
        check_book = super(TreasuryCheckbook, self).create(vals)
        for n in range(check_book.count):
            self.env['treasury.outgoing'].create({
                'number': '{}/{}'.format(check_book.series_no, int(check_book.first_serial_no) + n),
                'checkbook_id': check_book.id,
                'type': 'check'
            })
        return check_book

    @api.model
    def unlink(self):
        for checkbook in self:
            if any(check.state not in ('new', 'draft') for check in checkbook.check_ids):
                raise exceptions.UserError('There is at least one check with state other than new and draft.')
        return super(TreasuryCheckbook, self).unlink()

    @api.multi
    def action_cancel_all(self):
        for checkbook in self:
            checkbook.check_ids.filtered(lambda ch: ch.state in ('new', 'draft', 'printed')).write(
                {'state': 'canceled'})
            checkbook.active = False
