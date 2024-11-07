# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request


class CRMPortalController(CustomerPortal):
    @http.route(['/my/crm'], type='http', auth="user", website=True)
    def my_crm_portal(self, **kwargs):
        crm_obj = request.env['crm.lead']
        crm_datas = crm_obj.search([])
        vals = {
            'crm_datas': crm_datas,
            'page_name': 'crm_list_view'
        }
        return request.render('crm_portal.my_crm_portal', vals)

    @http.route(['/my/crm/<model("crm.lead"):crm_id>'], type='http', auth="user", website=True)
    def my_crm_portal_form_view(self, crm_id, **kwargs):
        pass



# class CrmPortal(http.Controller):
#     @http.route('/crm_portal/crm_portal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_portal/crm_portal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_portal.listing', {
#             'root': '/crm_portal/crm_portal',
#             'objects': http.request.env['crm_portal.crm_portal'].search([]),
#         })

#     @http.route('/crm_portal/crm_portal/objects/<model("crm_portal.crm_portal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_portal.object', {
#             'object': obj
#         })

