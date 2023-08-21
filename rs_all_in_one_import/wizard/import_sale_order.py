from odoo import models, api, fields, _
from odoo.exceptions import UserError, Warning
import base64
import io
import csv
import xlwt
import xlrd
from datetime import datetime
import getpass

class ImportSaleOrder(models.TransientModel):
    _name = "import.sale.order"
    _description = "Import Sale Order"

    file_type = fields.Selection([('csv file', 'CSV File'), ('xlsx file', 'XLSX File')], string='Select', default='csv file')
    stage_option = fields.Selection([('import draft quotation', 'Import Draft Quotation'),
                                     ('confirm quotation automatically with import', 'Confirm Quotation Automatically With Import')],
                                    string='Quotation Stage Option', default='import draft quotation')
    file = fields.Binary(string='File')
    filename = fields.Char('Select File')
    file_xls = fields.Binary(string='Report', readonly=True)
    flag = fields.Boolean(string="Flag")
    sequence_option = fields.Selection([('use excel/csv sequence number', 'Use Excel/CSV Sequence Number'),
                                        ('use system default sequence number', 'Use System Default Sequence Number')],
                                       string='Sequence Option', default='use excel/csv sequence number')
    import_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')],
                                         string='Import Product By', default='name')

    def import_sale_order(self):
        if self.file == False:
            raise UserError(_('Please upload the CSV or XLSX file only !!'))
        elif self.file_type == "csv file":
             try:
                 csv_data = base64.b64decode(self.file)
                 string_data = csv_data.decode('utf-8')
                 data_file = io.StringIO(string_data)
                 csv_reader = csv.reader(data_file, delimiter=',')
                 headers = {}
                 for row in csv_reader:
                     col_count = 0
                     for col in row:
                         headers[col] = col_count
                         col_count = col_count + 1
                     break;
                 for rows in csv_reader:

                     # Sale Order is already available
                     order_id = self.env['sale.order'].search([('name', '=', rows[headers['ORDER']].strip())])
                     if order_id:
                         raise UserError(_('ORDER ' + rows[headers['Order ID']].strip()+' is already exists in system !!'))
                     if not order_id:
                         # Check Partner available or not
                         customer = self.env['res.partner'].search([('name', '=', rows[headers['CUSTOMER']].strip())])
                         if not customer:
                             customer_dict = {'name': rows[headers['CUSTOMER']].strip()}
                             customer = self.env['res.partner'].create(customer_dict)
                         # Check Tax available or not
                         tax_id = self.env['account.tax'].search([('name', '=', rows[headers['TAX']].strip())])
                         if not tax_id:
                             tax_dict = {'name': rows[headers['TAX']].strip()}
                             if rows[headers['TAX']].strip() != '':
                                 tax_id = self.env['account.tax'].create(tax_dict)
                         # Check UOM Category available or not
                         uom_category_id = self.env['uom.category'].search([('name', '=', rows[headers['UOM']].strip())])
                         if not uom_category_id:
                             category_dict = {'name': rows[headers['UOM']].strip()}
                             uom_category_id = self.env['uom.category'].create(category_dict)
                         # Check UOM available or not
                         uom_id = self.env['uom.uom'].search([('name', '=', rows[headers['UOM']].strip()),
                                                              ('category_id', '=', uom_category_id.id)])
                         if not uom_id:
                             uom_disc = {'name': rows[headers['UOM']].strip(), 'category_id': uom_category_id.id}
                             uom_id = self.env['uom.uom'].create(uom_disc)
                         # Check Price List available or not
                         price_list_id = self.env['product.pricelist'].search([('name', '=', rows[headers['PRICELIST']].strip())])
                         if not price_list_id:
                             price_dict = {'name': rows[headers['PRICELIST']].strip()}
                             price_list_id = self.env['product.pricelist'].create(price_dict)
                         # Check Products available or not
                         if self.import_product_by == 'code':
                             product_id = self.env['product.product'].search([('default_code', '=', rows[headers['PRODUCT']].strip())])
                             if not product_id:
                                 prod_dict = {'name': rows[headers['PRODUCT']].strip(), 'default_code': rows[headers['PRODUCT']].strip()}
                                 product_id = self.env['product.template'].create(prod_dict)
                         elif self.import_product_by == 'name':
                             product_id = self.env['product.product'].search([('name', '=', rows[headers['PRODUCT']].strip())])
                             if not product_id:
                                 prod_dict = {'name': rows[headers['PRODUCT']].strip(), 'default_code': rows[headers['PRODUCT']].strip()}
                                 product_id = self.env['product.template'].create(prod_dict)
                         elif self.import_product_by == 'barcode':
                             product_id = self.env['product.product'].search([('barcode', '=', rows[headers['PRODUCT']].strip())])
                             if not product_id:
                                 prod_dict = {'name': rows[headers['PRODUCT']].strip(), 'default_code': rows[headers['PRODUCT']].strip(),
                                              'barcode': rows[headers['PRODUCT']].strip()}
                                 product_id = self.env['product.template'].create(prod_dict)
                         # Check Partner name available or not
                         x_partner_id = self.env['res.users'].search([('name', '=', rows[headers['x_partner_id@name']].strip())])

                         x_colors = self.env['partner.color'].search([('name', '=', rows[headers['x_color']].strip())])
                         if not x_colors:
                             color_dist = {'name': rows[headers['x_color']].strip()}
                             x_colors = self.env['partner.color'].create(color_dist)

                         line_vals = {
                             'product_id': product_id.id,
                             'name': rows[headers['DESCRIPTION']].strip(),
                             'product_uom_qty': int(rows[headers['QUANTITY']].strip()) if rows[headers['QUANTITY']].strip() else 0,
                             'price_unit': float(rows[headers['PRICE']].strip()) if rows[headers['PRICE']].strip() else 0,
                             'tax_id': tax_id if tax_id else False,
                             'uom_id': uom_id.id if uom_id.id else '',
                             'discount': rows[headers['DISCOUNT']].strip(),
                         }

                         # Check Date available or not
                         order_date = datetime.strptime(rows[headers['DATE']].strip(), "%Y/%m/%d")

                         if self.sequence_option == 'use excel/csv sequence number' and self.stage_option == 'import draft quotation':
                             order_vals = {
                                 'name': rows[headers['ORDER']].strip(),
                                 'partner_id': customer.id,
                                 'date_order': order_date,
                                 'pricelist_id': price_list_id.id,
                                 'x_partner_id': x_partner_id.id,
                                 'x_color': x_colors.id,
                                 'x_notes': rows[headers['x_notes']].strip(),
                                 'x_amount': rows[headers['x_amount']].strip(),
                                 'state': 'draft',
                                 'x_bool': rows[headers['x_bool']].strip(),
                                 'order_line': [(0, 0, line_vals)]
                             }
                         elif self.sequence_option == 'use excel/csv sequence number' and self.stage_option == 'confirm quotation automatically with import':
                             order_vals = {
                                 'name': rows[headers['ORDER']].strip(),
                                 'partner_id': customer.id,
                                 'date_order': order_date,
                                 'pricelist_id': price_list_id.id,
                                 'x_partner_id': x_partner_id.id,
                                 'x_color': x_colors.id,
                                 'x_notes': rows[headers['x_notes']].strip(),
                                 'x_amount': rows[headers['x_amount']].strip(),
                                 'state': 'sale',
                                 'x_bool': rows[headers['x_bool']].strip(),
                                 'order_line': [(0, 0, line_vals)]
                             }
                         elif self.sequence_option == 'use system default sequence number' and self.stage_option == 'import draft quotation':
                             order_vals = {
                                 'partner_id': customer.id,
                                 'date_order': order_date,
                                 'pricelist_id': price_list_id.id,
                                 'x_partner_id': x_partner_id.id,
                                 'x_color': x_colors.id,
                                 'x_notes': rows[headers['x_notes']].strip(),
                                 'x_amount': rows[headers['x_amount']].strip(),
                                 'state': 'draft',
                                 'x_bool': rows[headers['x_bool']].strip(),
                                 'order_line': [(0, 0, line_vals)]
                             }
                         elif self.sequence_option == 'use system default sequence number' and self.stage_option == 'confirm quotation automatically with import':
                             order_vals = {
                                 'partner_id': customer.id,
                                 'date_order': order_date,
                                 'pricelist_id': price_list_id.id,
                                 'x_partner_id': x_partner_id.id,
                                 'x_color': x_colors.id,
                                 'x_notes': rows[headers['x_notes']].strip(),
                                 'x_amount': rows[headers['x_amount']].strip(),
                                 'state': 'sale',
                                 'x_bool': rows[headers['x_bool']].strip(),
                                 'order_line': [(0, 0, line_vals)]
                             }
                         self.env['sale.order'].create(order_vals)
             except csv.Error:
                 raise UserError(_('Cannot determine the file format for the attached file.'))
        else:
            try:
                file_datas = base64.decodestring(self.file)
                workbook = xlrd.open_workbook(file_contents=file_datas)
                sheet = workbook.sheet_by_index(0)
                data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                data.pop(0)
                file_data = data
                for vals in file_data:
                    # Sale Order is already available
                    order_id = self.env['sale.order'].search([('name', '=', vals[0].strip())])
                    if order_id:
                        raise UserError(_('ORDER ' + vals[0].strip() + ' is already exists in system !!'))
                    if not order_id:
                        # Check Partner available or not
                        partner = self.env['res.partner'].search([('name', '=', vals[1].strip())])
                        print('-partner-', partner)
                        if not partner:
                            customer_vals = {'name': vals[1].strip()}
                            partner = self.env['res.partner'].create(customer_vals)
                        # Check Tax available or not
                        tax_id = self.env['account.tax'].search([('name', '=', vals[9])])
                        if not tax_id:
                            tax_dict = {'name': vals[9]}
                            if vals[9] != '':
                                tax_id = self.env['account.tax'].create(tax_dict)
                        # Check UOM Category available or not
                        uom_category_id = self.env['uom.category'].search([('name', '=', vals[5])])
                        if not uom_category_id:
                            category_dict = {'name': vals[5]}
                            uom_category_id = self.env['uom.category'].create(category_dict)
                        # Check UOM available or not
                        uom_id = self.env['uom.uom'].search([('name', '=', vals[5]),
                                                             ('category_id', '=', uom_category_id.id)])
                        if not uom_id:
                            uom_disc = {'name': vals[5], 'category_id': uom_category_id.id}
                            uom_id = self.env['uom.uom'].create(uom_disc)
                        # Check Price List available or not
                        price_list_id = self.env['product.pricelist'].search([('name', '=', vals[2])])
                        if not price_list_id:
                            price_dict = {'name': vals[2]}
                            price_list_id = self.env['product.pricelist'].create(price_dict)

                        # Check Products available or not
                        if self.import_product_by == 'code':
                            product_id = self.env['product.product'].search([('default_code', '=', vals[3])])
                            if not product_id:
                                prod_dict = {'name': vals[3], 'default_code': vals[3]}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'name':
                            product_id = self.env['product.product'].search([('name', '=', vals[3])])
                            if not product_id:
                                prod_dict = {'name': vals[3], 'default_code': vals[3]}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'barcode':
                            product_id = self.env['product.product'].search([('barcode', '=', vals[3])])
                            if not product_id:
                                prod_dict = {'name': vals[3], 'default_code': vals[3], 'barcode': vals[3]}
                                product_id = self.env['product.template'].create(prod_dict)
                        # Check Partner name available or not
                        x_partner_id = self.env['res.users'].search([('name', '=', vals[12])])

                        xx_colors = self.env['partner.color'].search([('name', '=', vals[14])])
                        if not xx_colors:
                            color_dist = {'name': vals[14]}
                            xx_colors = self.env['partner.color'].create(color_dist)

                        line_vals = {
                            'product_id': product_id.id,
                            'name': vals[6],
                            'product_uom_qty': int(vals[4]) if vals[4] else 0,
                            'price_unit': float(vals[7]) if vals[7] else 0,
                            'tax_id': tax_id if tax_id else False,
                            'uom_id': uom_id.id if uom_id.id else '',
                            'discount': vals[11],
                        }
                        # Check Date available or not
                        order_date = datetime.strptime(vals[10], "%Y/%m/%d")

                        if self.sequence_option == 'use excel/csv sequence number' and self.stage_option == 'import draft quotation':
                            order_vals = {
                                'name': vals[0],
                                'partner_id': partner.id,
                                'date_order': order_date,
                                'pricelist_id': price_list_id.id,
                                'x_partner_id': x_partner_id.id,
                                'x_color': xx_colors.id,
                                'x_notes': vals[15],
                                'x_amount': vals[16],
                                'state': 'draft',
                                'x_bool': vals[17],
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'use excel/csv sequence number' and self.stage_option == 'confirm quotation automatically with import':
                            order_vals = {
                                'name': vals[0],
                                'partner_id': partner.id,
                                'date_order': order_date,
                                'pricelist_id': price_list_id.id,
                                'x_partner_id': x_partner_id.id,
                                'x_color': xx_colors.id,
                                'x_notes': vals[15],
                                'x_amount': vals[16],
                                'state': 'sale',
                                'x_bool':  vals[17],
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'use system default sequence number' and self.stage_option == 'import draft quotation':
                            order_vals = {
                                'partner_id': partner.id,
                                'date_order': order_date,
                                'pricelist_id': price_list_id.id,
                                'x_partner_id': x_partner_id.id,
                                'x_color': xx_colors.id,
                                'x_notes': vals[15],
                                'x_amount': vals[16],
                                'state': 'draft',
                                'x_bool': vals[17],
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'use system default sequence number' and self.stage_option == 'confirm quotation automatically with import':
                            order_vals = {
                                'partner_id': partner.id,
                                'date_order': order_date,
                                'pricelist_id': price_list_id.id,
                                'x_partner_id': x_partner_id.id,
                                'x_color': xx_colors.id,
                                'x_notes': vals[15],
                                'x_amount': vals[16],
                                'state': 'sale',
                                'x_bool': vals[17],
                                'order_line': [(0, 0, line_vals)]
                            }
                    self.env['sale.order'].create(order_vals)
            except csv.Error:
                raise UserError(_('Cannot determine the file format for the attached file.'))

    def export_sale_order(self):
        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Sheet')
        s_h = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour yellow; align: horiz center")
        ws.write(0, 0, 'Order Id', s_h)
        ws.write(0, 1, 'Customer', s_h)
        ws.write(0, 2, 'Price List', s_h)
        ws.write(0, 3, 'Product', s_h)
        ws.write(0, 4, 'Quantity', s_h)
        ws.write(0, 5, 'UOM', s_h)
        ws.write(0, 6, 'Description', s_h)
        ws.write(0, 7, 'Price', s_h)
        ws.write(0, 8, 'Sales Person', s_h)
        ws.write(0, 9, 'Tax', s_h)
        ws.write(0, 10, 'Date', s_h)
        ws.write(0, 11, 'Discount', s_h)
        ws.write(0, 12, 'x_partner_id', s_h)
        # ws.write(0, 13, 'x_partner_ids', s_h)
        ws.write(0, 13, 'x_color', s_h)
        ws.write(0, 14, 'x_notes', s_h)
        ws.write(0, 15, 'x_amount', s_h)
        ws.write(0, 16, 'x_bool', s_h)

        sale_order_id = self.env['sale.order'].search([])
        if sale_order_id:
            row = 1
            for vals in sale_order_id:
                ws.write(row, 0, vals.name)
                ws.write(row, 1, vals.partner_id.name)
                ws.write(row, 2, '')
                ws.write(row, 3, vals.order_line.product_id.name)
                ws.write(row, 4, vals.order_line.product_uom_qty)
                ws.write(row, 5, vals.order_line.uom_id.name)
                ws.write(row, 6, vals.order_line.name)
                ws.write(row, 7, vals.order_line.price_unit)
                ws.write(row, 8, vals.user_id.name)
                ws.write(row, 9, vals.order_line.tax_id.name)
                ws.write(row, 10, vals.date_order)
                ws.write(row, 11, vals.order_line.discount)
                ws.write(row, 12, vals.x_partner_id.name)
                ws.write(row, 13, vals.x_color.name)
                ws.write(row, 14, vals.x_notes)
                ws.write(row, 15, vals.x_amount)
                ws.write(row, 16, vals.x_bool)
                row += 1
        else:
            raise Warning(_("Currently, There is no sale order !!"))

        filenames = 'Sale Order' + '.xls'
        workbook.save(filenames)
        file = open(filenames, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write({'filename': filenames, 'file_xls': out, 'flag': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def export_csv_sale_order(self):
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        csv_header = ['ORDER', 'CUSTOMER', 'PRICE LIST', 'PRODUCT', 'QUANTITY', 'UOM', 'DESCRIPTION', 'PRICE',
                      'SALESPERSON', 'TAX', 'DATE', 'DISCOUNT', 'x_partner_id@name', 'x_color', 'x_notes', 'x_amount',
                      'x_bool']
        csv_writer.writerow(csv_header)

        sale_order_ids = self.env['sale.order'].search([])
        if sale_order_ids:
            for vals in sale_order_ids:
                row = [
                    vals.name,
                    vals.partner_id.name,
                    '',
                    vals.order_line.product_id.name if vals.order_line.product_id else '',
                    vals.order_line.product_uom_qty if vals.order_line.product_uom_qty else 0,
                    vals.order_line.uom_id.name if vals.order_line.uom_id else False,
                    vals.order_line.name if vals.order_line else '',
                    vals.order_line.price_unit if vals.order_line else 0,
                    vals.user_id.name if vals.user_id else False,
                    ', '.join(vals.order_line.mapped('tax_id.name')) if vals.order_line else '',
                    vals.date_order.strftime('%Y-%m-%d') if vals.date_order else '',
                    vals.order_line.discount if vals.order_line else 00.00,
                    vals.x_partner_id.name if hasattr(vals, 'x_partner_id@name') else False,
                    vals.x_color.name if hasattr(vals, 'x_color') else False,
                    vals.x_notes if hasattr(vals, 'x_notes') else '',
                    vals.x_amount if hasattr(vals, 'x_amount') else 0,
                    vals.x_bool if hasattr(vals, 'x_bool') else False,
                ]
                csv_writer.writerow(row)
        else:
            raise Warning(_("Currently, There are no sale orders!"))
        csv_data = csv_buffer.getvalue()
        csv_buffer.close()
        csv_file_name = 'Sale Order.csv'
        return {
            'type': 'ir.actions.act_url',
            'res_model': 'purchase.wizard',
            'url': "data:text/csv;charset=utf-8," + csv_data,
            'res_id': self.id,
            'target': 'new',
            'filename': csv_file_name,
        }

class SaleOrderLine(models.Model):
    _inherit =  "sale.order.line"

    uom_id = fields.Many2one('uom.uom', string="UOM")