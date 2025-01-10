# -*- coding: utf-8 -*-
{
    'name': "CRM Portal",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'crm', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_portal_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'crm_portal/static/src/xml/modal_form_templates.xml',
            'crm_portal/static/src/css/style.css',
            # 'crm_portal/static/src/js/portal_modal.js',
            # 'crm_portal/static/src/js/ModalForm.js',  # Include the ModalForm.js file

        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
