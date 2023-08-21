from odoo import models, api, fields, _
from odoo.exceptions import UserError
import base64
import io
import csv
import xlrd
import xlwt


class AccountWizard(models.TransientModel):
    _name = 'import.account.move'

    file_type = fields.Selection([('csv_file', 'CSV file'), ('xls_file', 'XLS file')], string='Select', default='csv_file')
    type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier'),
                             ('customer_credit_note', 'Customer Credit Notes'),
                             ('vendor_credit_note', 'Vendor Credit Notes')], string='Type', default='customer')
    sequence_option = fields.Selection([('using_excel_csv', 'Use Excel/CSV Sequence Number'),
                                        ('using_default', 'Use System Default Sequence NUmber')],
                                       string='Sequence Option', default='using_excel_csv')
    import_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')],
                                         string='Import Product By', default='name')
    file = fields.Binary(string='File Upload')
    invoice_stage_option = fields.Selection([('import_draft_invoice', 'Import Draft Invoice'),
                                             ('validate_invoice_automatically_with_import',
                                              'Validate Invoice Automatically With Import')],
                                            string='Invoice Stage Option', default='import_draft_invoice')
    account_option = fields.Selection([('use_product_configuration', 'Use Account From Configuration'),
                                       ('use_account_from_excel_csv', 'Use Account From Excel/CSV')],
                                      string='Account Option')
    flag = fields.Boolean(string='Flag')
    filename = fields.Char(string='Select File ')
    file_xls = fields.Binary(string='Report', readonly='True')
    file_csv = fields.Binary(string='Report', readonly='True')

    def import_button(self):
        if self.file == False:
            raise UserError(_('Please upload the CSV or XLSX file only !!'))
        elif self.file_type == "csv_file":
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
                    # invoice is already available
                    order_id = self.env['account.move'].search([('name', '=', rows[headers['INVOICE ID']].strip())])
                    if order_id:
                        raise UserError(
                            _('INVOICE ID ' + rows[headers['INVOICE ID']].strip() + ' is already exists in system !!'))
                    if not order_id:

                        # Check Partner available or not
                        partner = self.env['res.partner'].search([('name', '=', rows[headers['PARTNER']].strip())])
                        if not partner:
                            customer_vals = {'name': rows[headers['PARTNER']].strip()}
                            partner = self.env['res.partner'].create(customer_vals)

                        # Check Tax available or not
                        tax_id = self.env['account.tax'].search([('name', '=', rows[headers['TAX']].strip())])
                        if not tax_id:
                            tax_dict = {'name': rows[headers['TAX']].strip()}
                            if rows[headers['TAX']].strip() != '':
                                tax_id = self.env['account.tax'].create(tax_dict)

                        # Check UOM Category available or not
                        uom_category_id = self.env['uom.category'].search(
                            [('name', '=', rows[headers['UOM']].strip())])
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
                        price_list_id = self.env['product.pricelist'].search(
                            [('name', '=', rows[headers['PRICE']].strip())])
                        if not price_list_id:
                            price_dict = {'name': rows[headers['PRICE']].strip()}
                            price_list_id = self.env['product.pricelist'].create(price_dict)

                        # Check Products available or not
                        if self.import_product_by == 'code':
                            product_id = self.env['product.product'].search(
                                [('default_code', '=', rows[headers['PRODUCT']].strip())])
                            if not product_id:
                                prod_dict = {'name': rows[headers['PRODUCT']].strip(),
                                             'default_code': rows[headers['PRODUCT']].strip()}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'name':
                            product_id = self.env['product.product'].search(
                                [('name', '=', rows[headers['PRODUCT']].strip())])
                            if not product_id:
                                prod_dict = {'name': rows[headers['PRODUCT']].strip(),
                                             'default_code': rows[headers['PRODUCT']].strip()}
                                product_id = self.env['product.template'].create(prod_dict)
                        elif self.import_product_by == 'barcode':
                            product_id = self.env['product.product'].search(
                                [('barcode', '=', rows[headers['PRODUCT']].strip())])
                            if not product_id:
                                prod_dict = {'name': rows[headers['PRODUCT']].strip(),
                                             'default_code': rows[headers['PRODUCT']].strip(),
                                             'barcode': rows[headers['PRODUCT']].strip()}
                                product_id = self.env['product.template'].create(prod_dict)

                        # Check Partner name available or not
                        k_partner_id = self.env['res.users'].search([('name', '=', rows[headers['k_partner_id@name']].strip())])

                        x_color = self.env['partner.color'].search([('name', '=', rows[headers['x_color']].strip())])
                        if not x_color:
                            color_dist = {'name': rows[headers['x_color']].strip()}
                            x_color = self.env['partner.color'].create(color_dist)

                        move_type = 'out_invoice'

                        if self.type == 'customer':
                            move_type = 'out_invoice'
                        elif self.type == 'supplier':
                            move_type = 'in_invoice'
                        elif self.type == 'customer_credit_note':
                            move_type = 'out_refund'
                        elif self.type == 'vendor_credit_note':
                            move_type = 'in_refund'
                        line_vals = {
                            'product_id': product_id[0].id,
                            'name': rows[headers['DESCRIPTION']].strip(),
                            'quantity': int(rows[headers['QUANTITY']].strip()) if rows[
                                headers['QUANTITY']].strip() else 0,
                            'price_unit': float(rows[headers['PRICE']].strip()) if rows[
                                headers['PRICE']].strip() else 0,
                            'tax_ids': tax_id if tax_id else False,
                            'discount': rows[headers['DISCOUNT']].strip(),
                        }

                        if self.sequence_option == 'using_excel_csv' and self.invoice_stage_option == 'import_draft_invoice':
                            order_vals = {
                                'name': rows[headers['INVOICE ID']].strip(),
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'color': x_color.name,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']].strip(),
                                'state': 'draft',
                                'move_type': move_type,
                                'boolean': rows[headers['x_bool']].strip(),
                                'invoice_line_ids': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_excel_csv' and self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                            order_vals = {
                                'name': rows[headers['INVOICE ID']].strip(),
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'color': x_color.name,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']].strip(),
                                'state': 'draft',
                                'move_type': move_type,
                                'invoice_line_ids': [(0, 0, line_vals)]
                            }

                        elif self.sequence_option == 'using_default' and self.invoice_stage_option == 'import_draft_invoice':
                            order_vals = {
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'color': x_color.name,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']].strip(),
                                'state': 'draft',
                                'move_type': move_type,
                                'invoice_line_ids': [(0, 0, line_vals)]
                            }
                        elif self.sequence_option == 'using_default' and self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                            order_vals = {
                                'partner_id': partner.id,
                                'partner_name': k_partner_id.id,
                                'color': x_color.name,
                                'notes': rows[headers['x_notes']].strip(),
                                'amount': rows[headers['x_amount']].strip(),
                                'state': 'draft',
                                'move_type': move_type,
                                'invoice_line_ids': [(0, 0, line_vals)]
                            }
                        invoice = self.env['account.move'].create(order_vals)
                        if self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                            invoice.action_post()
            except csv.Error:
                raise UserError(_('Cannot determine the file format for the attached file.'))

        elif self.file_type == "xls_file":
            # Excel import
            try:
                file_datas = base64.decodebytes(self.file)
                workbook = xlrd.open_workbook(file_contents=file_datas)
                sheet = workbook.sheet_by_index(0)
                data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                data.pop(0)
                file_data = data

                for vals in file_data:
                    order_id = self.env['account.move'].search([('name', '=', vals[0].strip())])
                    if order_id:
                        raise UserError(_('INVOICE ID ' + vals[0].strip() + ' already exists in the system!!'))

                    if not order_id:
                        partner = self.env['res.partner'].search([('name', '=', vals[1].strip())])
                        if not partner:
                            customer_vals = {'name': vals[1].strip()}
                            partner = self.env['res.partner'].create(customer_vals)

                        tax_id = self.env['account.tax'].search([('name', '=', vals[2].strip())])
                        if not tax_id:
                            tax_dict = {'name': str(vals[2]).strip()}
                            tax_id = self.env['account.tax'].create(tax_dict)

                        price_list_id = self.env['product.pricelist'].search([('name', '=', str(vals[8]).strip())])
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

                        move_type = 'out_invoice'  # Default move_type for regular invoices

                        if self.type == 'customer':
                            move_type = 'out_invoice'
                        elif self.type == 'supplier':
                            move_type = 'in_invoice'
                        elif self.type == 'customer_credit_note':
                            move_type = 'out_refund'
                        elif self.type == 'vendor_credit_note':
                            move_type = 'in_refund'

                        line_vals = {
                            'product_id': product_id[0].id,
                            'name': vals[7].strip(),
                            'quantity': str(vals[5]).strip(),
                            'price_unit': str(vals[8]).strip(),
                            'tax_ids': tax_id if tax_id else False,
                            # 'uom_id': uom_id.id if uom_id.id else '',
                            'discount': str(vals[12]).strip(),
                        }
                        print('---------line----------------', line_vals)

                    partner_name = self.env['res.users'].search([('name', '=', vals[13].strip())])
                    print('----------nnnnnnnnnnnnnnn', partner_name)
                    if self.sequence_option == 'using_excel_csv' and self.invoice_stage_option == 'import_draft_invoice':
                        order_vals = {
                            'name': vals[0].strip(),
                            'partner_id': partner.id,
                            'partner_name': partner_name,
                            # 'price_list_id': str(vals[8]).strip(),
                            'notes': vals[16].strip(),
                            'amount': int(vals[17]),
                            'state': 'draft',
                            'color': vals[15],
                            'boolean': str(vals[18]).strip(),
                            'move_type': move_type,
                            'invoice_line_ids': [(0, 0, line_vals)]

                        }
                    elif self.sequence_option == 'using_excel_csv' and self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                        order_vals = {
                            'name': vals[0].strip(),
                            'partner_id': partner.id,
                            # 'price_list_id': str(vals[8]).strip(),
                            'notes': vals[16].strip(),
                            'amount': int(vals[17]),
                            'state': 'draft',
                            # 'color': vals[15],
                            'boolean': str(vals[18]).strip(),
                            'move_type': move_type,
                            'invoice_line_ids': [(0, 0, line_vals)]

                        }
                    elif self.sequence_option == 'using_default' and self.invoice_stage_option == 'import_draft_invoice':
                        order_vals = {
                            # 'name': vals[0].strip(),
                            'partner_id': partner.id,
                            # 'price_list_id': str(vals[8]).strip(),
                            'notes': vals[16].strip(),
                            'amount': int(vals[17]),
                            'state': 'draft',
                            # 'color': vals[15],
                            'boolean': str(vals[18]).strip(),
                            'move_type': move_type,
                            'invoice_line_ids': [(0, 0, line_vals)]

                        }
                    elif self.sequence_option == 'using_default' and self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                        order_vals = {
                            # 'name': vals[0].strip(),
                            'partner_id': partner.id,
                            # 'price_list_id': str(vals[8]).strip(),
                            'notes': vals[16].strip(),
                            'amount': int(vals[17]),
                            'state': 'draft',
                            # 'color': vals[15],
                            'boolean': str(vals[18]).strip(),
                            'move_type': move_type,
                            'invoice_line_ids': [(0, 0, line_vals)]

                        }

                    invoice = self.env['account.move'].create(order_vals)
                    if self.invoice_stage_option == 'validate_invoice_automatically_with_import':
                        invoice.action_post()

            except xlrd.XLRDError:
                raise UserError(_('Cannot determine the file format for the attached file.'))
        else:
            raise UserError(_('Unsupported file type. Please upload a CSV or XLSX file.'))

    def download_excel_button(self):
        print('-----EXPORT------')

        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Sheet')
        s_h = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour yellow; align: horiz center")
        print("---------------------------------writing into sheet--------------------")

        # Write field names as headers in the first row
        field_names = ['INVOICE ID', 'PARTNER', 'Account', 'PRODUCT', 'QUANTITY', 'UOM', 'DESCRIPTION',
                       'PRICE', 'SALESPERSON', 'TAX', 'DATE', 'DISCOUNT', 'k_partner_id',
                       'k_partner_ids', 'x_color', 'x_notes', 'x_amount', 'x_bool']

        for col, field_name in enumerate(field_names):
            ws.write(0, col, field_name, s_h)

        if self.type == 'customer':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        elif self.type == 'supplier':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'in_invoice')])
        elif self.type == 'customer_credit_note':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_refund')])
        elif self.type == 'vendor_credit_note':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'in_refund')])
        else:
            raise UserError(_('Please select a valid Type to proceed!'))

        # invoice_ids = self.env['account.move'].search([])
        print('so----', invoice_ids)

        if invoice_ids:
            row = 1
            for invoice in invoice_ids:
                print('--------invoice--', invoice, invoice.partner_name, invoice.partner_id.name)
                partner_data = invoice.partner_id
                for line in invoice.invoice_line_ids:
                    ws.write(row, 0, invoice.name)
                    ws.write(row, 1, partner_data.name)
                    ws.write(row, 2, partner_data.property_account_payable_id.display_name)
                    ws.write(row, 3, line.product_id.name)
                    ws.write(row, 4, line.quantity)
                    ws.write(row, 5, line.product_uom_id.name)
                    ws.write(row, 6, line.name)
                    ws.write(row, 7, line.price_unit)
                    ws.write(row, 8, invoice.invoice_user_id.name)
                    tax_names = ', '.join(line.tax_ids.mapped('name'))  # Concatenate tax names
                    ws.write(row, 9, tax_names)
                    ws.write(row, 10, '')
                    ws.write(row, 11, line.discount)
                    # ws.write(row, 12, invoice.partner_name)
                    # ws.write(row, 13, partner_data.k_partner_ids)
                    ws.write(row, 14, invoice.color)
                    ws.write(row, 15, invoice.notes)
                    ws.write(row, 16, invoice.amount)
                    ws.write(row, 17, invoice.boolean)
                    row += 1
        else:
            raise UserError(_("Currently, There are no invoices!"))

        filename = 'Invoice Order.xls'
        workbook.save(filename)
        with open(filename, "rb") as file:
            file_data = file.read()
        out = base64.encodebytes(file_data)
        self.write({'filename': filename, 'file_xls': out, 'flag': True})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.account.move',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def download_csv_button(self):
        print('-----EXPORT INVOICE------')

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        csv_header = [
            'INVOICE ID', 'PARTNER', 'ACCOUNT', 'PRODUCT', 'QUANTITY', 'UOM', 'DESCRIPTION',
            'PRICE', 'SALESPERSON', 'TAX', 'DATE', 'DISCOUNT', 'K_PARTNER_ID',
            'K_PARTNER_IDS', 'X_COLOR', 'X_NOTES', 'X_AMOUNT', 'X_BOOL'
        ]
        csv_writer.writerow(csv_header)

        if self.type == 'customer':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        elif self.type == 'supplier':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'in_invoice')])
        elif self.type == 'customer_credit_note':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_refund')])
        elif self.type == 'vendor_credit_note':
            invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        else:
            raise UserError(_('Please select a valid Type to proceed!'))

        # invoice_ids = self.env['account.move'].search([])
        print('invoice_ids:', invoice_ids)
        if invoice_ids:
            for invoice in invoice_ids:
                partner_data = invoice.partner_id
                for line in invoice.invoice_line_ids:
                    row = [
                        invoice.name,
                        partner_data.name,
                        partner_data.property_account_payable_id.display_name,
                        line.product_id.name,
                        line.quantity,
                        line.product_uom_id.name,
                        line.name,
                        line.price_unit,
                        invoice.invoice_user_id.name,
                        ', '.join(line.tax_ids.mapped('name')),
                        invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else '',
                        line.discount,
                        invoice.partner_name.name,'',
                        # partner_data.k_partner_ids,
                        invoice.color,
                        invoice.notes,
                        invoice.amount,
                        invoice.boolean,
                    ]
                    csv_writer.writerow(row)
        else:
            raise Warning("Currently, there are no invoices!")

        csv_data = csv_buffer.getvalue()
        csv_buffer.close()

        csv_file_name = 'invoices.csv'
        return {
            'type': 'ir.actions.act_url',
            'url': "data:text/csv;charset=utf-8," + csv_data,
            'target': 'new',
            'filename': csv_file_name,
        }
