from odoo import models, api, fields, _
from odoo.exceptions import UserError
import base64
import io
import csv
import xlrd
import xlwt
import codecs


class PurchaseWizard(models.TransientModel):
    _name = 'import.purchase.order'

    sequence_option = fields.Selection([('using_excel_csv', 'Use Excel/CSV Sequence Number'),
                                        ('using_default', 'Use System Default Sequence Number')],
                                       default='using_excel_csv',
                                       string='Sequence Option')
    import_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')], default='name',
                                         string='Import Product By')
    file = fields.Binary(string='File')
    purchase_stage_option = fields.Selection([('import_draft_purchase', 'Import Draft Purchase'),
                                              ('confirm_purchase_automatically_with_import',
                                               'Confirm Purchse Automatically with Import')],
                                             default='import_draft_purchase', string='Purchase Stage Option')
    file_type = fields.Selection([('csv file', 'CSV File'), ('xlsx file', 'XLSX File')], default='csv file',
                                 string='Select')
    filename = fields.Char('Select File')
    flag = fields.Boolean(string="Flag")
    file_xls = fields.Binary(string="File Xls", readonly='True')

    def import_purchase_order(self):
        if self.file == False:
            raise UserError(_('Please upload the CSV or XLSX file only!!'))
        elif self.file_type == "csv file":
            try:
                csv_data = base64.b64decode(self.file)
                string_data = codecs.decode(csv_data, 'utf-8-sig')
                # string_data = csv_data.decode('utf-8-sig')
                # Use 'utf-8-sig' encoding
                data_file = io.StringIO(string_data)
                csv_reader = csv.reader(data_file, delimiter=',')
                headers = {}
                # headers = {col: col_count for col_count, col in enumerate(next(csv_reader))}

                for row in csv_reader:
                    col_count = 0
                    for col in row:
                        headers[col] = col_count
                        col_count = col_count + 1
                    break

                for rows in csv_reader:
                    order_id = self.env['purchase.order'].search([('name', '=', rows[headers['PURCHASE ID']].strip())])
                    if order_id:
                        raise UserError(
                            _('PURCHASE ID ' + rows[
                                headers['PURCHASE ID']].strip() + ' already exists in the system!!'))

                    if not order_id:

                        partner = self.env['res.partner'].search([('name', '=', rows[headers['SUPPLIER']].strip())])
                        if not partner:
                            customer_vals = {'name': rows[headers['SUPPLIER']].strip()}
                            partner = self.env['res.partner'].create(customer_vals)

                        tax_id = self.env['account.tax'].search([('name', '=', rows[headers['TAX']].strip())])
                        print('---tax---', tax_id)
                        if not tax_id:
                            tax_dict = {'name': rows[headers['TAX']].strip()}
                            if rows[headers['TAX']].strip() != '':
                                tax_id = self.env['account.tax'].create(tax_dict)
                        uom_category_id = self.env['uom.category'].search([('name', '=', rows[headers['UOM']].strip())])
                        if not uom_category_id:
                            category_dict = {'name': rows[headers['UOM']].strip()}
                            uom_category_id = self.env['uom.category'].create(category_dict)

                        uom_id = self.env['uom.uom'].search([('name', '=', rows[headers['UOM']].strip()),
                                                             ('category_id', '=', uom_category_id.id)])
                        if not uom_id:
                            uom_disc = {'name': rows[headers['UOM']].strip(), 'category_id': uom_category_id.id}
                            uom_id = self.env['uom.uom'].create(uom_disc)

                        price_list_id = self.env['product.pricelist'].search(
                            [('name', '=', rows[headers['PRICE']].strip())])
                        if not price_list_id:
                            price_dict = {'name': rows[headers['PRICE']].strip()}
                            price_list_id = self.env['product.pricelist'].create(price_dict)

                        if self.import_product_by == 'code':
                            product_id = self.env['product.product'].search(
                                [('default_code', '=', rows[headers['PROD']].strip())])
                            if not product_id:
                                prod_dict = {'name': rows[headers['PROD']].strip(),
                                             'default_code': rows[headers['PROD']].strip()}
                                product_id = self.env['product.template'].create(prod_dict)
                        if self.import_product_by == 'name':
                            product_id = self.env['product.product'].search(
                                [('name', '=', rows[headers['PROD']].strip())])
                            print('-------------prod-', product_id)
                            if not product_id:
                                prod_dict = {'name': rows[headers['PROD']].strip(),
                                             'default_code': rows[headers['PROD']].strip()}
                                print('ddddddddddd', prod_dict)
                                product_id = self.env['product.template'].create(prod_dict)
                                print('------create--', product_id)
                        elif self.import_product_by == 'barcode':
                            product_id = self.env['product.product'].search(
                                [('barcode', '=', rows[headers['PROD']].strip())])
                            if not product_id:
                                prod_dict = {'name': rows[headers['PROD']].strip(),
                                             'default_code': rows[headers['PROD']].strip(),
                                             'barcode': rows[headers['PROD']].strip()}
                                product_id = self.env['product.template'].create(prod_dict)

                        k_partner_id = self.env['res.users'].search(
                            [('name', '=', rows[headers['k_partner_id@name']].strip())])

                        line_vals = {
                            # 'product_id': product_id.id,
                            'product_id': product_id[0].id,

                            'name': rows[headers['DESCRIPTION']].strip(),
                            'product_qty': int(rows[headers['QUANTITY']].strip()) if rows[
                                headers['QUANTITY']].strip() else 0,
                            'price_unit': float(rows[headers['PRICE']].strip()) if rows[
                                headers['PRICE']].strip() else 0,
                            'taxes_id': tax_id if tax_id else False,
                            # 'discount': rows[headers['DISCOUNT']].strip(),
                        }
                        print('---------line----------------', line_vals)

                        order_vals = {}
                        if self.sequence_option == 'using_excel_csv' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                'name': rows[headers['PURCHASE ID']].strip(),
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'notes': rows[headers['x_notes']].strip(),
                                'colors': rows[headers['x_color']].strip(),
                                'amount': rows[headers['x_amount']],
                                'state': 'draft',
                                # 'move_type': 'out_invoice',
                                'order_line': [(0, 0, line_vals)]
                            }


                        # print('---------line----------------', line_vals)
                        elif self.sequence_option == 'using_excel_csv' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                'name': rows[headers['PURCHASE ID']].strip(),
                                'partner_id': partner.sudo().id,
                                'partner_name': k_partner_id.id,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']],
                                'state': 'purchase',
                                # 'move_type': 'out_invoice',
                                'order_line': [(0, 0, line_vals)]
                            }

                        elif self.sequence_option == 'using_default' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                # 'name': rows[headers['PURCHASE ID']].strip(),
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']],
                                'state': 'draft',
                                # 'move_type': 'out_invoice',
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_default' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                # 'name': rows[headers['PURCHASE ID']].strip(),
                                'partner_id': partner.sudo().id,
                                'partner_name': k_partner_id.id,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']],
                                'state': 'purchase',
                                # 'move_type': 'out_invoice',
                                'order_line': [(0, 0, line_vals)]
                            }
                        self.env['purchase.order'].create(
                            order_vals)  # if self.purchase_stage_option_stage == 'confirm_purchase_automatically_with_import':
            except csv.Error:
                raise UserError(_('Cannot determine the file format for the attached file.'))

        elif self.file_type == "xlsx file":
            # Excel import
            try:
                file_datas = base64.decodebytes(self.file)
                workbook = xlrd.open_workbook(file_contents=file_datas)
                sheet = workbook.sheet_by_index(0)
                data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                data.pop(0)
                file_data = data

                for vals in file_data:
                    order_id = self.env['purchase.order'].search([('name', '=', vals[0].strip())])
                    if order_id:
                        raise UserError(_('PURCHASE ID ' + vals[0].strip() + ' already exists in the system!!'))

                    if not order_id:
                        partner = self.env['res.partner'].search([('name', '=', vals[1].strip())])
                        print('partner---->', partner)
                        if not partner:
                            customer_vals = {'name': vals[1].strip()}
                            partner = self.env['res.partner'].create(customer_vals)
                            print('--not partner--', partner)

                        tax_id = self.env['account.tax'].search([('name', '=', vals[8].strip())])
                        if not tax_id:
                            tax_dict = {'name': str(vals[8]).strip()}
                            tax_id = self.env['account.tax'].create(tax_dict)

                        price_list_id = self.env['product.pricelist'].search([('name', '=', str(vals[7]).strip())])
                        if not price_list_id:
                            price_dict = {'name': str(vals[8]).strip()}
                            price_list_id = self.env['product.pricelist'].create(price_dict)

                        if self.import_product_by == 'code':
                            product_id = self.env['product.product'].search(
                                [('default_code', '=', vals[3].strip())])
                            if not product_id:
                                prod_dict = {'name': vals[3].strip(),
                                             'default_code': vals[3].strip()}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'name':
                            product_id = self.env['product.product'].search(
                                [('name', '=', vals[3].strip())])
                            if not product_id:
                                prod_dict = {'name': vals[3].strip(),
                                             'default_code': vals[3].strip()}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'barcode':
                            product_id = self.env['product.product'].search(
                                [('barcode', '=', vals[3].strip())])
                            if not product_id:
                                prod_dict = {'name': vals[3].strip(),
                                             'default_code': vals[3].strip(),
                                             'barcode': vals[3].strip()}
                                product_id = self.env['product.template'].create(prod_dict)

                        k_partner_id = self.env['res.users'].search(
                            [('name', '=', vals[10].strip())])

                        line_vals = {
                            'product_id': product_id[0].id,
                            'name': str(vals[6]).strip() if vals[6] else '',
                            'product_qty': int(vals[4]) if vals[4] else 0,
                            'price_unit': float(vals[7]) if isinstance(vals[7], (int, float)) else 0,
                            'taxes_id': tax_id if tax_id else False,
                        }

                        if self.sequence_option == 'using_excel_csv' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                'name': str(vals[0]).strip() if vals[0] else '',
                                'partner_name': k_partner_id.id,
                                'partner_id': partner.id,
                                'notes': vals[13].strip(),
                                'colors': vals[12].strip(),
                                'amount': vals[7],
                                'state': 'draft',
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_excel_csv' and self.purchase_stage_option == 'confirm_purchase_automatically_with_import':
                            order_vals = {
                                'name': vals[0].strip(),
                                'partner_id': partner.id,
                                'notes': vals[13].strip(),
                                'colors': vals[12].strip(),
                                'amount': vals[7],
                                'state': 'purchase',
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_default' and self.purchase_stage_option == 'import_draft_purchase':
                            order_vals = {
                                'partner_id': partner.id,

                                'notes': vals[13].strip(),
                                'colors': vals[12].strip(),
                                'amount': vals[7],
                                'state': 'draft',
                                'order_line': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_default' and self.purchase_stage_option == 'confirm_purchase_automatically_with_import':
                            order_vals = {
                                'partner_id': partner.id,
                                'notes': vals[13].strip(),
                                'colors': vals[12].strip(),
                                'amount': vals[7],
                                'state': 'purchase',
                                'order_line': [(0, 0, line_vals)]
                            }

                    self.env['purchase.order'].create(order_vals)
            except xlrd.XLRDError:
                raise UserError(_('Cannot determine the file format for the attached file.'))
        else:
            raise UserError(_('Unsupported file type. Please upload a CSV or XLSX file.'))

    def export_csv_purchase_order(self):
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        csv_header = [
            'PURCHASE ID', 'SUPPLIER', 'CURRENCY', 'PROD', 'QUANTITY', 'UOM',
            'DESCRIPTION', 'PRICE', 'TAX', 'DATE', 'COLORS', 'BOOLEAN', 'AMOUNT', 'NOTES'
        ]
        csv_writer.writerow(csv_header)

        purchase_order_ids = self.env['purchase.order'].search([])
        if purchase_order_ids:
            for vals in purchase_order_ids:
                row = [
                    vals.name,
                    vals.partner_id.name,
                    vals.currency_id.name if vals.currency_id else '',
                    vals.product_id.name if vals.product_id else '',
                    vals.order_line[0].product_qty if vals.order_line else 0,
                    '',  # UOM field - update with appropriate value
                    vals.order_line[0].name if vals.order_line else '',
                    vals.order_line[0].price_unit if vals.order_line else 0,
                    ', '.join(vals.order_line.mapped('taxes_id.name')) if vals.order_line else '',
                    vals.date_order.strftime('%Y-%m-%d') if vals.date_order else '',
                    vals.colors if hasattr(vals, 'colors') else '',  # Include 'colors' field
                    vals.boolean if hasattr(vals, 'boolean') else False,  # Include 'boolean' field
                    vals.amount if hasattr(vals, 'amount') else 0,  # Include 'amount' field
                    vals.notes if hasattr(vals, 'notes') else '',  # Include 'notes' field
                ]
                csv_writer.writerow(row)
        else:
            raise Warning(_("Currently, There are no purchase orders!"))

        csv_data = csv_buffer.getvalue()
        csv_buffer.close()

        csv_file_name = 'purchase_orders.csv'

        return {
            'type': 'ir.actions.act_url',
            'res_model': 'purchase.wizard',
            'url': "data:text/csv;charset=utf-8," + csv_data,
            'res_id': self.id,
            'target': 'new',
            'filename': csv_file_name,
        }

    def export_excel_purchase_order(self):
        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Sheet')
        s_h = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour yellow; align: horiz center")

        csv_header = [
            'PURCHASE ID', 'SUPPLIER', 'CURRENCY', 'PROD', 'QUANTITY', 'UOM',
            'DESCRIPTION', 'PRICE', 'TAX', 'DATE', 'COLORS', 'BOOLEAN', 'AMOUNT', 'NOTES'
        ]
        for col, header in enumerate(csv_header):
            ws.write(0, col, header, s_h)

        purchase_order_ids = self.env['purchase.order'].search([])
        print('purchase_order_ids:', purchase_order_ids)
        if purchase_order_ids:
            row = 1
            for vals in purchase_order_ids:
                csv_row = [
                    vals.name,
                    vals.partner_id.name,
                    vals.currency_id.name if vals.currency_id else '',
                    vals.product_id.name if vals.product_id else '',
                    vals.order_line[0].product_qty if vals.order_line else 0,
                    '',  # UOM field - update with appropriate value
                    vals.order_line[0].name if vals.order_line else '',
                    vals.order_line[0].price_unit if vals.order_line else 0,
                    ', '.join(vals.order_line.mapped('taxes_id.name')) if vals.order_line else '',
                    vals.date_order.strftime('%Y-%m-%d') if vals.date_order else '',
                    vals.colors if hasattr(vals, 'colors') else '',  # Include 'colors' field
                    vals.boolean if hasattr(vals, 'boolean') else False,  # Include 'boolean' field
                    vals.amount if hasattr(vals, 'amount') else 0,  # Include 'amount' field
                    vals.notes if hasattr(vals, 'notes') else '',  # Include 'notes' field
                ]
                for col, value in enumerate(csv_row):
                    ws.write(row, col, value)
                row += 1
        else:
            raise Warning(_("Currently, There are no purchase orders!"))

        filename = 'purchase_orders.xls'
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write({'filename': filename, 'file_xls': out, 'flag': True})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.purchase.order',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }