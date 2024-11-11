# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from collections import OrderedDict
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils


class CRMPortalController(CustomerPortal):

    def _crm_get_date_ranges(self):
        today = datetime.today()

        values = {
            'all': {
                'label': _('All'),
                'start_date': None,
                'end_date': None,
            },
            'closed_last_year': {
                'label': _('Closed Last Year'),
                'start_date': today.replace(year=today.year - 1, month=1, day=1),
                'end_date': today.replace(year=today.year - 1, month=12, day=31),
            },
            'closed_last_week': {
                'label': _('Closed Last Week'),
                'start_date': date_utils.start_of(today - timedelta(weeks=1), 'week'),
                'end_date': date_utils.end_of(today - timedelta(weeks=1), 'week'),
            },
            'closed_last_month': {
                'label': _('Closed Last Month'),
                'start_date': date_utils.start_of(today - relativedelta(months=1), 'month'),
                'end_date': date_utils.end_of(today - relativedelta(months=1), 'month'),
            },
            'closed_this_month': {
                'label': _('Closed This Month'),
                'start_date': date_utils.start_of(today, 'month'),
                'end_date': date_utils.end_of(today, 'month'),
            },
            'closed_this_week': {
                'label': _('Closed This Week'),
                'start_date': date_utils.start_of(today, 'week'),
                'end_date': date_utils.end_of(today, 'week'),
            },
            'closed_this_year': {
                'label': _('Closed This Year'),
                'start_date': today.replace(month=1, day=1),
                'end_date': today.replace(month=12, day=31),
            },
            'closed_this_quarter': {
                'label': _('Closed This Quarter'),
                'start_date': date_utils.start_of(today, 'quarter'),
                'end_date': date_utils.end_of(today, 'quarter'),
            },
            'closed_today': {
                'label': _('Closed Today'),
                'start_date': today.date(),
                'end_date': today.date(),
            }
        }

        return values
    def _crm_get_searchbar_sortings(self):
        values = {
            'create_date desc': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 10},
            'name': {'label': _('Title'), 'order': 'name', 'sequence': 20},
            'stage_id': {'label': _('Stage'), 'order': 'stage_id', 'sequence': 30},
            'expected_revenue desc': {'label': _('Amount'), 'order': 'expected_revenue desc', 'sequence': 40},
            'priority desc': {'label': _('Priority'), 'order': 'priority desc', 'sequence': 50},
            'date_deadline asc': {'label': _('Deadline'), 'order': 'date_deadline asc', 'sequence': 60},
        }
        return values

    @http.route(['/my/crm', '/my/crm/page/<int:page>'], type='http', auth="user", website=True)
    def my_crm_portal(self, page=1, sortby=None, filterby=None, **kwargs):
        sorted_list = self._crm_get_searchbar_sortings()
        if not sortby:
            sortby = 'create_date desc'
        order_by = sorted_list[sortby]['order']
        crm_obj = request.env['crm.lead']

        search_filter = self._crm_get_date_ranges()
        if not filterby:
            filterby = 'all'
        selected_range = search_filter.get(filterby, search_filter['all'])

        date_domain = []
        if selected_range['start_date'] and selected_range['end_date']:
            date_domain = [('date_deadline', '>=', selected_range['start_date']),
                           ('date_deadline', '<=', selected_range['end_date'])]

        domain = [('user_id', '!=', False)] + date_domain
        crm_cnt = crm_obj.search_count(domain)

        pager_details = pager(
            url='/my/crm',
            total=crm_cnt,
            url_args={'sortby': sortby, 'filterby': filterby},
            page=page,
            step=10
        )
        crm_datas = crm_obj.search(domain, limit=10, order=order_by, offset=pager_details['offset'])

        vals = {
            'crm_datas': crm_datas,
            'page_name': 'crm_list_view',
            'pager': pager_details,
            'default_url': '/my/crm',
            'sortby': sortby,
            'searchbar_sortings': sorted_list,
            'filterby': filterby,
            'searchbar_filters': OrderedDict(sorted(search_filter.items())),
        }
        return request.render('crm_portal.my_crm_portal', vals)

    @http.route(['/my/crm/<model("crm.lead"):crm_id>'], type='http', auth="user", website=True)
    def my_crm_portal_form_view(self, crm_id, **kwargs):
        vals = {
            'crm_id': crm_id,
            'page_name': 'crm_form_view'
        }

        crm_records = request.env['crm.lead'].search([])
        crm_ids = crm_records.ids
        crm_index = crm_ids.index(crm_id.id)
        if crm_index != 0 and crm_ids[crm_index-1]:
            vals['prev_record'] = '/my/crm/%s' % crm_ids[crm_index-1]
        if crm_index < len(crm_ids)-1 and crm_ids[crm_index+1]:
            vals['next_record'] = '/my/crm/%s' % crm_ids[crm_index+1]


        return request.render('crm_portal.my_crm_portal_form_view', vals)

