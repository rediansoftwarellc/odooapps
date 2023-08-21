from io import StringIO, BytesIO
import xlrd as xlrd
from odoo import models, fields, api, _
import csv
import base64
from odoo.exceptions import UserError
import xlsxwriter


class MrpWizard(models.TransientModel):
    _name = 'import.bom'

    import_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')],
                                         string='Import Product By', default='name')
    import_material_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')],
                                                  string='Import Material Product By', default='name')
    bom_type = fields.Selection([('normal', 'Normal'), ('phantom', 'Phantom')], string='Bom Type', default='normal')
    file = fields.Binary(string='File')
    file_type = fields.Selection([('csv file', 'CSV File'), ('xlsx file', 'XLSX File')], string='Select', default='csv file')
    filename = fields.Char('Select File')
    flag = fields.Boolean(string="Flag")
    file_xls = fields.Binary(string="File Xls", readonly='True')

    def import_mrp_bom(self):
        if not self.file:
            raise UserError(_('Please upload a CSV or XLSX file only!!'))

        elif self.file_type == "csv file":
            try:
                csv_data = base64.b64decode(self.file)
                string_data = csv_data.decode('utf-8')
                data_file = StringIO(string_data)
                csv_reader = csv.DictReader(data_file, delimiter=',')

                for row in csv_reader:
                    main_product_ref = row.get('Main Product', '').strip()
                    material_product_ref = row.get('Material Product', '').strip()

                    bom_product_id = self._get_product_id(main_product_ref, self.import_product_by)
                    line_product_id = self._get_product_id(material_product_ref, 'name')  # Always search by name

                    if not bom_product_id:
                        raise UserError(_('Product with reference %s not found in the system!' % main_product_ref))

                    if line_product_id == bom_product_id:
                        raise UserError(
                            _('The BoM line product [%s] cannot be the same as the BoM product.' % material_product_ref))

                    if not line_product_id:
                        raise UserError(_('Product with reference %s not found in the system!' % material_product_ref))

                    bom_line_vals = {
                        'product_id': line_product_id.id,
                        'product_qty': int(row.get('Quantity ', '0').strip()),
                        'product_uom_id': line_product_id.uom_id.id if line_product_id.uom_id else False,
                    }

                    # Search for an existing BoM with the same product
                    existing_bom = self.env['mrp.bom'].search(
                        [('product_tmpl_id', '=', bom_product_id.product_tmpl_id.id)], limit=1)

                    if existing_bom:
                        # If a BoM already exists for the main product, add the line to it
                        existing_bom.bom_line_ids = [(0, 0, bom_line_vals)]
                    else:
                        # Create a new BoM if one doesn't exist
                        partner_id = self.env['res.users'].search([('name', '=', row.get('x_partner_id@name', '').strip())])
                        bom_vals = {
                            'product_tmpl_id': bom_product_id.product_tmpl_id.id if bom_product_id.product_tmpl_id else False,
                            'product_id': bom_product_id.id if bom_product_id else False,
                            'type': self.bom_type,
                            'notes': row.get('x_notes', '').strip(),
                            'color': row.get('x_color', '').strip(),
                            'amount': row.get('x_amount', '').strip(),
                            'boolean': row.get('x_bool', '').strip(),
                            'partner_name': partner_id.id,
                            'bom_line_ids': [(0, 0, bom_line_vals)],
                        }
                        print ('----------bom-', bom_vals)
                        bom_vals['bom_line_ids'] = [(0, 0, bom_line_vals)]
                        self.env['mrp.bom'].create(bom_vals)
            except csv.Error:
                raise UserError(_('Cannot determine the file format for the attached file.'))
        elif self.file_type == "xlsx file":
            try:
                excel_data = base64.b64decode(self.file)
                data_file = BytesIO(excel_data)
                workbook = xlrd.open_workbook(file_contents=data_file.read())
                sheet = workbook.sheet_by_index(0)
                csv_reader = self._excel_to_dict(sheet)
                self._process_bom_data(csv_reader)
            except xlrd.XLRDError:
                raise UserError(_('Cannot determine the file format for the attached file.'))

    def _process_bom_data(self, data):
        for row in data:
            main_product_ref = row.get('Main Product', '').strip()
            material_product_ref = row.get('Material Product', '').strip()
            bom_product_id = self._get_product_id(main_product_ref, self.import_product_by)
            line_product_id = self._get_product_id(material_product_ref, 'name')  # Always search by name

            if not bom_product_id:
                raise UserError(_('Product with reference %s not found in the system!' % main_product_ref))

            if line_product_id == bom_product_id:
                raise UserError(

                    _('The BoM line product [%s] cannot be the same as the BoM product.' % material_product_ref))

            if not line_product_id:
                raise UserError(_('Product with reference %s not found in the system!' % material_product_ref))

            bom_line_vals = {
                'product_id': line_product_id.id,
                'product_qty': int(row.get('Material Qty', '0').strip()),
                'product_uom_id': line_product_id.uom_id.id if line_product_id.uom_id else False,
            }

            # Search for an existing BoM with the same product
            existing_bom = self.env['mrp.bom'].search(
                [('product_tmpl_id', '=', bom_product_id.product_tmpl_id.id)], limit=1)

            if existing_bom:
                # If a BoM already exists for the main product, add the line to it
                existing_bom.bom_line_ids = [(0, 0, bom_line_vals)]
            else:
                # Create a new BoM if one doesn't exist
                bom_vals = {
                    'product_tmpl_id': bom_product_id.product_tmpl_id.id if bom_product_id.product_tmpl_id else False,
                    'product_id': bom_product_id.id if bom_product_id else False,
                    'notes': row.get('x_notes', ''),
                    'color': row.get('x_color', ''),
                    'amount': row.get('x_amount', ''),
                    'type': self.bom_type,
                    'bom_line_ids': [(0, 0, bom_line_vals)],
                }
                self.env['mrp.bom'].create(bom_vals)

    def _get_product_id(self, product_name, import_product_by):
        product_domain = []
        if import_product_by == 'name':
            product_domain = [('name', '=', product_name.strip())]
        elif import_product_by == 'code':
            product_domain = [('default_code', '=', product_name.strip())]
        elif import_product_by == 'barcode':
            product_domain = [('barcode', '=', product_name.strip())]

        product_id = self.env['product.product'].sudo().search(product_domain, limit=1)
        return product_id or False

    def _excel_to_dict(self, sheet):
        data = []
        headers = [cell.value for cell in sheet.row(0)]
        for row in range(1, sheet.nrows):
            row_data = {}
            for col in range(sheet.ncols):
                row_data[headers[col]] = sheet.cell_value(row, col)
            data.append(row_data)
        return data

    def export_csv_mrp_bom(self):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        csv_header = [
            'Main Product', 'Material Product', 'Quantity', 'UOM',
            'Partner Name', 'Color', 'Boolean', 'Amount', 'Notes',
        ]
        csv_writer.writerow(csv_header)

        bom_records = self.env['mrp.bom'].search([])
        if not bom_records:
            raise UserError(_("Currently, There are no Bill of Materials (BOM)!"))

        for bom in bom_records:
            for line in bom.bom_line_ids:
                row = [
                    bom.product_id.display_name if bom.product_id else '',
                    line.product_id.display_name if line.product_id else '',
                    line.product_qty,
                    line.product_uom_id.name if line.product_uom_id else '',
                    bom.partner_name.name if bom.partner_name else '',
                    bom.color,
                    bom.boolean,
                    bom.amount if bom.amount is not False else '',
                    bom.notes,
                ]
                csv_writer.writerow(row)

        csv_data = csv_buffer.getvalue()
        csv_buffer.close()

        csv_file_name = 'mrp_bom.csv'

        return {
            'type': 'ir.actions.act_url',
            'res_model': 'import.bom',
            'url': "data:text/csv;charset=utf-8," + csv_data,
            'res_id': self.id,
            'target': 'new',
            'filename': csv_file_name,
        }

    def export_excel_mrp_bom(self):
        workbook = xlsxwriter.Workbook('mrp_bom.xlsx')
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})
        worksheet.write_row(0, 0,
                            ['Main Product', 'Material Product', 'Quantity', 'UOM', 'Partner Name', 'Color', 'Boolean',
                             'Amount', 'Notes'], bold)

        bom_records = self.env['mrp.bom'].search([])
        if not bom_records:
            raise UserError(_("Currently, There are no Bill of Materials (BOM)!"))

        row = 1
        for bom in bom_records:
            for line in bom.bom_line_ids:
                worksheet.write(row, 0, bom.product_id.display_name if bom.product_id else '')
                worksheet.write(row, 1, line.product_id.display_name if line.product_id else '')
                worksheet.write(row, 2, line.product_qty)
                worksheet.write(row, 3, line.product_uom_id.name if line.product_uom_id else '')
                worksheet.write(row, 4, bom.partner_name.name if bom.partner_name else '')
                worksheet.write(row, 5, bom.color)
                worksheet.write(row, 6, bom.boolean)
                worksheet.write(row, 7, bom.amount)
                worksheet.write(row, 8, bom.notes)
                row += 1

        workbook.close()

        with open('mrp_bom.xlsx', 'rb') as file:
            file_data = file.read()

        return {
            'type': 'ir.actions.act_url',
            'res_model': 'import.bom',
            'url': "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + base64.b64encode(
                file_data).decode(),
            'res_id': self.id,
            'target': 'new',
            'filename': 'mrp_bom.xlsx',
        }
