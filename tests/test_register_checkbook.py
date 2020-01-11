from odoo.tests.common import TransactionCase, tagged, Form
import datetime
from odoo.tools import jadatetime as jd


@tagged('-at_install', 'post_install')
class TestRegisterCheckBook(TransactionCase):
    def setUp(self):
        super(TestRegisterCheckBook, self).setUp()
        self.checkbook = self.env['treasury.checkbook'].create({
            'journal_id': 8,
            'series_no': 1234,
            'first_serial_no': 123456,
            'select_count': 'custom_count',
            'count': 6
        })

        self.checkbook_ct = self.env['treasury.checkbook'].create({
            'journal_id': 8,
            'series_no': 9874,
            'first_serial_no': 65421,
            'select_count': 'custom_count',
            'count': 8
        })

    def test_register_checkbook(self):
        """
        when register a checkbook, all checks should be created and in new state
        """
        self.assertEqual(len(self.checkbook.check_ids), 6)
        self.assertEqual(
            sorted([check.name for check in self.checkbook.check_ids]),
            [('{}/{}'.format(self.checkbook.series_no, int(self.checkbook.first_serial_no) + n))
             for n in range(self.checkbook.count)])
        self.assertEqual(all(item == 'new' for item in [check.state for check in self.checkbook.check_ids]), True)

    def test_remained_check(self):
        """
        checkbook # remained should be correct when some checks state are changed
        """
        self.assertEqual(self.checkbook.remained, 6)
        self.checkbook.check_ids[0].state, self.checkbook.check_ids[1].state = 'delivered', 'printed'
        self.assertEqual(self.checkbook.remained, 4)

    def test_checkbook_state(self):
        """
        checkbook state should change when all checks are issued and when all checks are cleaned/canceled
        """
        self.checkbook.check_ids.write({'state': 'printed'})
        self.assertEqual(self.checkbook.state, 'finished')
        self.checkbook.check_ids.write({'state': 'canceled'})
        self.assertEqual(self.checkbook.state, 'done')
        self.checkbook.check_ids.write({'state': 'cleaned'})
        self.assertEqual(self.checkbook.state, 'done')

    def test_checkbook_count(self):
        """
        checkbook count should be correct when selecting it from a list and when it has custom value.
        """
        self.assertEqual(self.checkbook.count, 6)

        ch_t = Form(self.env['treasury.checkbook'])
        ch_t.journal_id = self.env['account.journal'].browse(8)
        ch_t.series_no = 4567
        ch_t.first_serial_no = 456789
        ch_t.select_count = '10'

        self.assertEqual(ch_t.count, 10)
        self.checkbook_test = ch_t.save()

        self.assertEqual(self.checkbook_test.count, 10)

        with self.assertRaises(AssertionError):
            with Form(self.checkbook) as ch:
                ch.select_count = '20'

    def test_check_amount_text(self):
        """
        check amount should be correct in written in Persian
        """
        self.checkbook.check_ids[0].amount = 1363
        self.assertEqual(self.checkbook.check_ids[0].amount_text, 'یک هزار و سیصد و شصت و سه')

    def test_check_date_due_text(self):
        """
        check date should be correct in written in Persian
        """
        self.checkbook.check_ids[0].date_due = datetime.date(2020, 1, 4)
        self.checkbook.check_ids[1].date_due = jd.date(1398, 11, 14).togregorian()
        self.assertEqual(self.checkbook.check_ids[0].date_due_text, 'چهاردهم دی یک هزار و سیصد و نود و هشت')
        self.assertEqual(self.checkbook.check_ids[1].date_due_text, 'چهاردهم بهمن یک هزار و سیصد و نود و هشت')

    def test_cancel_all(self):
        self.checkbook_ct.check_ids[0].state = 'delivered'
        self.checkbook_ct.check_ids[1].state = 'cleaned'
        self.checkbook_ct.check_ids[2].state = 'bounced'
        self.checkbook_ct.check_ids[3].state = 'draft'
        self.checkbook_ct.check_ids[4].state = 'printed'
        self.assertEqual(len(self.checkbook_ct.check_ids.filtered(lambda x: x.state in ('new', 'draft', 'printed'))), 5)
        self.checkbook_ct.cancel_all()
        self.assertEqual(len(self.checkbook_ct.check_ids.filtered(lambda x: x.state in ('new', 'draft', 'printed'))), 0)
        self.assertEqual(len(self.checkbook_ct.check_ids.filtered(lambda x: x.state == 'canceled')), 5)
        self.assertEqual(self.checkbook_ct.active, False)
