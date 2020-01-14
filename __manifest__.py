{
    'name': 'treasury',
    'version': '1.0',
    'category': 'Localization',
    'description': """
    """,
    'author': "Maryam Kia",
    'website': "",
    'depends': ['account'

                ],
    'data': ['security/treasury_groups.xml',
             'security/ir.model.access.csv',
             'report/print_check.xml',
             'report/check_report.xml',
             'data/ir_sequence_data.xml',
             'views/treasury_menus.xml',
             'views/treasury_checkbook_views.xml',
             'views/treasury_check_views.xml',
             'views/treasury_incoming_views.xml',
             ],
    'demo': [],
}
