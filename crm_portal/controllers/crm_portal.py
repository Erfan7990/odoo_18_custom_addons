# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from collections import OrderedDict
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter


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

    def _crm_get_search_list(self, search):
        values = {
             'All': {'input': 'all', 'label': _('All'), 'domain': []},
            'name': {'input': 'name', 'label': _('Search in Name'), 'domain': [('name', 'ilike', '%' + search + '%')]},
            'expected_revenue': {'input': 'expected_revenue', 'label': _('Search in Revenue'), 'domain': [('expected_revenue', 'ilike', '%' + search + '%')]},
            'stage_id': {'input': 'stage_id', 'label': _('Search in Stage'), 'domain': [('stage_id.name', 'ilike', '%' + search + '%')]},
            'priority': {'input': 'priority', 'label': _('Search in Priority'), 'domain': [('priority', 'ilike', '%' + search + '%')]},
            'partner_id': {'input': 'partner_id', 'label': _('Search in Customer'), 'domain': [('partner_id.name', 'ilike', '%' + search + '%')]},
        }
        return values

    def _crm_get_searchbar_groupby(self):
        values = {
            'none': {'input': 'none','label': _('None')},
            'stage_id': {'input': 'stage_id', 'label': _('Stage')},
            'contact_name': {'input': 'contact_name', 'label': _('Contact Name')},
            'user_id': {'input': 'user_id', 'label': _('Salesperson')},
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
    def my_crm_portal(self, page=1, sortby=None, filterby=None, groupby=None, search='', search_in='All', **kwargs):
        sorted_list = self._crm_get_searchbar_sortings()
        group_list = self._crm_get_searchbar_groupby()
        search_list = self._crm_get_search_list(search)
        if not sortby:
            sortby = 'create_date desc'
        if not groupby:
            groupby = 'stage_id'

        order_by = sorted_list[sortby]['order']
        crm_obj = request.env['crm.lead']
        crm_group_by = group_list.get(groupby, {})
        search_domain = search_list.get(search_in, {}).get('domain', [])
        if not search_domain:
            search_in = 'All'
            search_domain = search_list.get('All', {}).get('domain', [])

        if groupby in ('stage_id', 'contact_name', 'user_id'):
            crm_group_by = crm_group_by.get('input')
            order_by = crm_group_by + "," + order_by
        else:
            crm_group_by = ''


        search_filter = self._crm_get_date_ranges()
        if not filterby:
            filterby = 'all'
        selected_range = search_filter.get(filterby, search_filter['all'])

        date_domain = []
        if selected_range['start_date'] and selected_range['end_date']:
            date_domain = [('date_deadline', '>=', selected_range['start_date']),
                           ('date_deadline', '<=', selected_range['end_date'])]

        domain = [('user_id', '!=', False)] + date_domain
        if search_domain:
            domain = domain + search_domain
        if groupby == 'none':
            crm_cnt = crm_obj.search_count(domain)
            pager_details = pager(
                url='/my/crm',
                total=crm_cnt,
                url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search': search, 'search_in': search_in},
                page=page,
                step=10
            )
            crm_datas = crm_obj.search(domain, limit=10, order=order_by, offset=pager_details['offset'])
        else:
            crm_datas = crm_obj.search(domain, order=order_by)
            pager_details = None

        if crm_group_by:
            crm_group_list = [{crm_group_by: k, 'crm_datas': crm_obj.concat(*g)} for k,g in groupbyelem(crm_datas, itemgetter(crm_group_by))]
        else:
            crm_group_list = [{'crm_datas': crm_datas}]


        vals = {
            'group_crms': crm_group_list,
            'crm_datas': crm_datas,
            'page_name': 'crm_list_view',
            'pager': pager_details,
            'default_url': '/my/crm',
            'sortby': sortby,
            'searchbar_sortings': sorted_list,
            'searchbar_groupby': group_list,
            'searchbar_inputs': search_list,
            'filterby': filterby,
            'groupby': groupby,
            'search': search,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(search_filter.items())),
        }
        return request.render('crm_portal.my_crm_portal', vals)

    @http.route(['/my/crm/<model("crm.lead"):crm_id>'], type='http', auth="user", website=True)
    def my_crm_portal_form_view(self, crm_id, **kwargs):
        order_id = request.env['sale.order'].search([('origin', '=', crm_id.name)])
        vals = {
            'order_id': order_id,
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

    @http.route(['/edit/crm/<model("crm.lead"):crm_id>'], method=["POST", "GET"], type='http', auth="user", website=True)
    def my_crm_portal_edit_form_view(self, crm_id, **kwargs):
        states = request.env['res.country.state'].search([])
        countries = request.env['res.country'].search([])
        teams = request.env['crm.team'].search([])
        tags = request.env['crm.tag'].search([])
        campaigns = request.env['utm.campaign'].search([])
        medias = request.env['utm.medium'].search([])
        sources = request.env['utm.source'].search([])
        partner_ids = request.env['res.partner'].search([])
        vals = {
            'crm_id': crm_id,
            'page_name': 'crm_edit_form_view',
            'states': states,
            'countries': countries,
            'teams': teams,
            'tags': tags,
            'campaigns': campaigns,
            'medias': medias,
            'sources': sources,
            'partner_ids': partner_ids,
        }
        val_list={}
        crm_records = request.env['crm.lead'].search([('id', '=', crm_id.id)])
        if request.httprequest.method == 'POST':
            partner_id = kwargs.get('partner_id')
            state_id = kwargs.get('state_id')
            country_id = kwargs.get('country_id')
            team_id = kwargs.get('team_id')
            tag_ids = kwargs.get('tag_ids')
            campaign_id = kwargs.get('campaign_id')
            medium_id = kwargs.get('medium_id')
            source_id = kwargs.get('source_id')
            if crm_id.partner_id.id == int(partner_id):
                val_list['name'] = kwargs.get('name') or False
                val_list['email_from'] = kwargs.get('email_from') or False
                val_list['phone'] = kwargs.get('phone') or False
                val_list['street'] = kwargs.get('street') or False
                val_list['city'] = kwargs.get('city') or False
                val_list['state_id'] = int(state_id) if state_id and state_id.strip() else False
                val_list['zip'] = kwargs.get('zip') or False
                val_list['country_id'] = int(country_id) if country_id and country_id.strip() else False
                val_list['partner_name'] = kwargs.get('partner_name') or False
                val_list['website'] = kwargs.get('website') or False
                val_list['team_id'] = int(team_id) if team_id and team_id.strip() else False
                val_list['tag_ids'] = [int(tag_ids) if tag_ids and tag_ids.strip() else False]
                val_list['campaign_id'] = int(campaign_id) if campaign_id and campaign_id.strip() else False
                val_list['contact_name'] = kwargs.get('contact_name') or False
                val_list['medium_id'] = int(medium_id) if medium_id and medium_id.strip() else False
                val_list['source_id'] = int(source_id) if source_id and source_id.strip() else False
                val_list['referred'] = kwargs.get('referred') or False
            else:
                val_list['partner_id'] = int(partner_id) if partner_id and partner_id.strip() else False
                val_list['campaign_id'] = int(campaign_id) if campaign_id and campaign_id.strip() else False
                val_list['medium_id'] = int(medium_id) if medium_id and medium_id.strip() else False
                val_list['source_id'] = int(source_id) if source_id and source_id.strip() else False
                val_list['referred'] = kwargs.get('referred') or False
            crm_records.write(val_list)
            return request.redirect('/my/crm/%s' % crm_id.id)



        return request.render('crm_portal.crm_portal_edit_form_view', vals)

    @http.route(['/my/quotation/<model("crm.lead"):crm_id>/<model("sale.order"):order_id>'], type='http', auth='user', website=True)
    def my_quotation_form(self, order_id, crm_id, **kw):
        vals = {
            'crm_id': crm_id,
            'order_id': order_id,
            'page_name': 'my_quotation_form',
        }
        return request.render('crm_portal.crm_quotation_form_view', vals)

    @http.route(['/my/crm/<model("crm.lead"):crm_id>/new/quotation'], type='http', method=["POST", "GET"], auth='user', website=True)
    def create_new_quotation(self, crm_id, **kwargs):
        payment_term_ids = request.env['account.payment.term'].search([])
        product_ids = request.env['product.product'].search([('type', '=', 'service')])
        vals = {
            'product_ids': product_ids,
            'payment_term_ids': payment_term_ids,
            'crm_id': crm_id,
            'page_name': 'new_quotation_create_form',
        }

        if request.httprequest.method == 'POST':
            partner_id = crm_id.partner_id.id
            validity_date = kwargs.get('validity_date')
            date_order = kwargs.get('date_order')
            payment_term_ids = kwargs.get('payment_term_ids')
            product_ids = kwargs.get('product_ids')
            quantity = kwargs.get('quantity')
            discount = kwargs.get('discount') if kwargs.get('discount') else '0'
            unit_price = kwargs.get('unit_price')
            try:
                # Convert validity_date to a date object
                validity_date = datetime.strptime(validity_date, '%Y-%m-%d').date() if validity_date else None
                # Convert date_order to a datetime object (correct format with 'T')
                date_order = datetime.strptime(date_order, '%Y-%m-%dT%H:%M') if date_order else None
            except ValueError as e:
                # Handle invalid date/datetime formats
                return request.render('crm_portal.error_page', {
                    'error_message': f"Invalid date format: {e}"
                })
            uom_id = request.env['product.product'].search([('id', '=', int(product_ids))]).uom_id
            val_list = {
                'partner_id': partner_id,
                'validity_date': validity_date,
                'date_order': date_order,
                'origin': crm_id.name,
                'payment_term_id': int(payment_term_ids),
                'order_line': [(0,0, {
                    'product_id': int(product_ids),
                    'product_uom_qty': int(quantity),
                    'product_uom': uom_id.id,
                    'discount': float(discount),
                    'price_unit': float(unit_price),
                })]
            }
            order_id = request.env['sale.order'].create(val_list)
            return request.redirect('/my/quotation/%s/%s' % (crm_id.id, order_id.id))

        return request.render('crm_portal.crm_create_new_quotation',vals)


    @http.route(['/new/crm'], type='http', method=["POST", "GET"], auth='user', website=True)
    def create_new_crm(self, **kwargs):


        partner_ids = request.env['res.partner'].sudo().search([])
        tag_ids = request.env['crm.tag'].sudo().search([])
        salesperson_id = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
        priority = [
            ('0', 'Low'),
            ('1', 'Medium'),
            ('2', 'High'),
            ('3', 'Very High'),
        ]

        vals = {
            'page_name': 'crm_form_create',
            'partner_ids': partner_ids,
            'tag_ids': tag_ids,
            'priority': priority,
            'salesperson_id': salesperson_id,
        }
        if request.httprequest.method == 'POST':
            if kwargs.get('tag_ids'):
                tag_values = [int(id) for id in kwargs.get('tag_ids').split(',')]
            else:
                tag_values = []
            partner_id = int(kwargs.get('partner_ids'))
            exist_partner_id = request.env['res.partner'].search([('id', '=', partner_id)])
            vals_list = {
                'name': kwargs.get('name'),
                'expected_revenue': kwargs.get('expected_revenue'),
                'partner_id': exist_partner_id.id,
                'user_id': salesperson_id.id,
                'date_deadline': kwargs.get('date_deadline'),
                'priority': kwargs.get('priority'),
                'tag_ids': tag_values,

            }
            if vals_list:
                crm_id = request.env['crm.lead'].create(vals_list)

        return request.render('crm_portal.my_crm_portal_create_new_crm', vals)