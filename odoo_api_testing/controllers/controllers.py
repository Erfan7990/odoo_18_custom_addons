# /your_module_name/controllers/main.py

from odoo import http
from odoo.http import request


class CustomApiController(http.Controller):

    # 1. Define the Route/URL
    @http.route('/api/products', type='json', auth='user', methods=['POST', 'GET'], csrf=False)
    def get_products_data(self, **kwargs):

        limit = kwargs.get('limit', 10)

        Product = request.env['product.template']

        products = Product.sudo().search_read(
            domain=[('sale_ok', '=', True)],  # Example filter
            fields=['id', 'name', 'list_price'],
            limit=limit
        )

        return {
            'status': 'success',
            'count': len(products),
            'data': products
        }

    @http.route('/api/products/<int:product_id>', type='json', auth='user', methods=['POST', 'GET'], csrf=False)
    def get_product_by_id(self, product_id, **kwargs):

        Product = request.env['product.template'].sudo()

        # 1. Use the read method to fetch the record directly by its ID
        # 'read' takes a list of IDs and returns a list of dictionaries.
        product = Product.browse(product_id).read(['id', 'name', 'list_price'])

        if not product:
            # 2. Handle case where ID is not found
            return {
                'status': 'error',
                'message': f'Product with ID {product_id} not found.'
            }

        # 3. Return the first (and only) dictionary in the list
        return {
            'status': 'success',
            'data': product[0]
        }

    @http.route(
        # Same URL as read-by-ID, but different method
        '/api/products/<int:product_id>',

        # IMPORTANT: Set methods to 'PUT'
        methods=['PATCH'],

        type='json',
        auth='user',
        csrf=False
    )
    def update_product(self, product_id, **kwargs):

        # 1. Get the recordset for the product ID
        Product = request.env['product.template'].sudo()
        product_record = Product.browse(product_id)

        if not product_record.exists():
            return {
                'status': 'error',
                'message': f'Product with ID {product_id} not found.'
            }

        # 2. Extract the data fields to be updated from the kwargs (Postman body)
        # kwargs contains the JSON body sent by the user (e.g., {"list_price": 550.0})
        update_data = kwargs

        if not update_data:
            return {
                'status': 'error',
                'message': 'No data provided for update.'
            }

        try:
            # 3. Call the Odoo 'write' method
            # Odoo's write method updates the record with the dictionary data
            product_record.write(update_data)

            # 4. Return success and the new, updated data
            # Re-read the record to show the client the updated state
            updated_product = product_record.read(['id', 'name', 'list_price', 'description_sale'])[0]

            return {
                'status': 'success',
                'message': f'Product {product_id} updated successfully.',
                'data': updated_product
            }
        except Exception as e:
            # 5. Handle potential Odoo validation errors
            return {
                'status': 'error',
                'message': 'Update failed due to server error or validation.',
                'details': str(e)
            }