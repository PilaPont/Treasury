{
    'name': 'Treasury',
    'version': '14.0.0.0.1.0+210228',
    'category': 'Accounting',
    'description': """
    To handle checks and bonds
    """,
    'author': "Kenevist Developers, Maryam Kia",
    'website': "www.kenevist.ir",
    'license': 'OPL-1',
    'depends': ['l10n_ir', 'account'
                ],
    'data': ['security/treasury_groups.xml',
             'security/ir.model.access.csv',
             'data/account_journal_data.xml',
             'data/ir_sequence_data.xml',
             'data/treasury_security_type_data.xml',
             'report/print_check.xml',
             'report/check_report.xml',
             'views/treasury_checkbook_views.xml',
             'views/treasury_outgoing_views.xml',
             'views/treasury_incoming_views.xml',
             'views/treasury_menus.xml',
             'views/res_config_settings_views.xml',
             'views/res_company_views.xml',
             ],
    'demo': [],
}
