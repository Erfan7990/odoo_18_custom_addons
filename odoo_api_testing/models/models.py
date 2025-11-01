# -*- coding: utf-8 -*-
import requests
import json
import base64
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class odoo_api_testing(models.Model):
    _inherit = 'product.template'
    _description = 'odoo_api_testing'

    api_id = fields.Integer(string='External ID')

    def fetch_product_info_from_api(self):
        """Fetch products from external API and insert them in bulk."""
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param('external_api.url')

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            _logger.error(f"API request failed: {e}")
            return

        data = response.json()
        products = data.get('products', [])  # fetch only first N records
        new_records = []
        failed = 0

        for record in products:
            api_id = record.get('id')
            if self.search_count([('api_id', '=', api_id)]):
                continue

            # Try to download image but skip if fails
            image_data = False
            image_url = record.get('images')[0] if record.get('images') else False
            if image_url:
                try:
                    img_response = requests.get(image_url, timeout=5)
                    if img_response.status_code == 200:
                        image_data = base64.b64encode(img_response.content)
                except Exception as img_err:
                    failed += 1
                    _logger.warning(f"Image skipped for {record.get('title')}: {img_err}")

            vals = {
                'name': record.get('title'),
                'default_code': record.get('sku'),
                'list_price': record.get('price') or 0.0,
                'api_id': api_id,
                'image_1920': image_data,
            }
            new_records.append(vals)

        if new_records:
            self.create(new_records)
            _logger.info(f"✅ Imported {len(new_records)} products successfully.")
        _logger.info(f"⚠️ {failed} images were skipped due to slow or failed downloads.")
