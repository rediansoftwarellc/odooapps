from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import csv
import xlrd
import xlwt


class StockLocation(models.Model):
    _inherit = 'stock.location'

    zone = fields.Boolean(string='Is Zone')


class InventoryWizard(models.TransientModel):
    _name = 'import.stock.picking'

    file_type = fields.Selection([('csv_file', 'CSV file'), ('xls_file', 'XLS file')], string='Select',
                                 default='csv_file')
    file = fields.Binary(string='File Upload')
    picking_type = fields.Many2one('stock.picking.type', string='Picking Type')
    import_product_by = fields.Selection([('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')],
                                         string='Import Product By', default='name')
    source_location_zone = fields.Many2one('stock.location', string='Source Location zone')
    dest_location_zone = fields.Many2one('stock.location', string='Destination Location Zone')
    flag = fields.Boolean(string='Flag')
    filename = fields.Char(string='Select File ')
    file_xls = fields.Binary(string='Report', readonly='True')

    def import_button(self):
        if not self.file:
            raise UserError(_('Please upload the CSV or XLSX file only!'))

        if self.file_type == 'csv_file':
            try:
                csv_data = base64.b64decode(self.file)
                string_data = csv_data.decode('ISO-8859-1')
                data_file = io.StringIO(string_data)
                csv_reader = csv.DictReader(data_file)

                for row in csv_reader:
                    name = row['NAME'].strip()  # Using 'NAME' from CSV as the 'name' for the stock picking
                    product_name = row['PRODUCT'].strip()
                    product_qty = float(row['QUANTITY'].strip()) if row['QUANTITY'].strip() else 0
                    product_uom_name = row['UOM'].strip()  # Assuming 'UOM' is the column for the Unit of Measure
                    customer_name = row['CUSTOMER'].strip()
                    origin = row['SOURCE DOCUMENT'].strip()
                    x_partner_name = row['x_partner_id@name'].strip()

                    customer = self.env['res.partner'].search([('name', '=', customer_name)], limit=1)
                    if not customer:
                        customer = self.env['res.partner'].create({'name': customer_name})

                    # Get or create the products based on the provided information
                    product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                    if not product:
                        product = self.env['product.product'].create({'name': product_name})

                    # Get or create the source and destination locations based on the provided information
                    source_location = self.source_location_zone
                    if not source_location:
                        raise UserError(_('Source location zone not found.'))

                    dest_location = self.dest_location_zone
                    if not dest_location:
                        raise UserError(_('Destination location zone not found.'))

                    # Get or create the Unit of Measure based on the provided information
                    uom = self.env['uom.uom'].search([('name', '=', product_uom_name)], limit=1)
                    if not uom:
                        raise UserError(_('Unit of Measure not found.'))

                    # Create stock picking based on the provided information
                    partner_id = self.env['res.users'].search([('name', '=', x_partner_name)])
                    picking = self.env['stock.picking'].create({
                        'name': name,  # Using the 'NAME' field from the CSV as the 'name' for the stock picking
                        'picking_type_id': self.picking_type.id,
                        'location_id': source_location.id,
                        'location_dest_id': dest_location.id,
                        'partner_id': customer.id,
                        'origin': origin,
                        # 'partner_name': customer_name,  # Store the value in the custom field
                        'color': row['COLOR'],  # Replace 'COLOR' with the correct header for the 'color' field
                        'boolean': row['BOOLEAN'],  # Replace 'BOOLEAN' with the correct header for the 'boolean' field
                        'amount': int(row['AMOUNT']),  # Replace 'AMOUNT' with the correct header for the 'amount' field
                        'notes': row['NOTES'],  # Rep
                        'partner_name': partner_id.name,
                    })

                    # Add stock move for the picked product
                    move_vals = {
                        'name': product.name,
                        'product_id': product.id,
                        'product_uom_qty': product_qty,
                        'product_uom': uom.id,  # Set the product UoM here
                        'picking_id': picking.id,
                        'location_id': source_location.id,
                        'location_dest_id': dest_location.id,
                    }
                    self.env['stock.move'].create(move_vals)

            except csv.Error:
                raise UserError(_('Cannot determine the file format for the attached file.'))

        elif self.file_type == 'xls_file':
            try:
                workbook = xlrd.open_workbook(file_contents=base64.b64decode(self.file))
                sheet = workbook.sheet_by_index(0)

                for row_num in range(1, sheet.nrows):  # Start from row 1 to skip headers
                    row = sheet.row_values(row_num)
                    name = row[0].strip()  # Assuming the 'NAME' column is in the first position (index 0) in XLS
                    product_name = row[4].strip()  # Assuming the 'PRODUCT' column is in the second position (index 1)
                    product_qty = row[5]
                    product_uom_name = row[7]  # Assuming 'UOM' is in the fourth position (index 3)
                    customer_name = row[1].strip()
                    origin = row[2].strip()
                    partner_name = row[12].strip()

                    customer = self.env['res.partner'].search([('name', '=', customer_name)], limit=1)
                    if not customer:
                        customer = self.env['res.partner'].create({'name': customer_name})

                    # Get or create the products based on the provided information
                    product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                    if not product:
                        product = self.env['product.product'].create({'name': product_name})

                    # Get or create the source and destination locations based on the provided information
                    source_location = self.source_location_zone
                    if not source_location:
                        raise UserError(_('Source location zone not found.'))

                    dest_location = self.dest_location_zone
                    if not dest_location:
                        raise UserError(_('Destination location zone not found.'))

                    # Get or create the Unit of Measure based on the provided information
                    uom = self.env['uom.uom'].search([('name', '=', str(product_uom_name))], limit=1)
                    if not uom:
                        raise UserError(_('Unit of Measure not found.'))

                    # Create stock picking based on the provided information
                    picking = self.env['stock.picking'].create({
                        'name': name,  # Using the 'NAME' field from the CSV as the 'name' for the stock picking
                        'picking_type_id': self.picking_type.id,
                        'location_id': source_location.id,
                        'location_dest_id': dest_location.id,
                        'partner_id': customer.id,
                        'origin': origin,
                        'color': row[8],  # Replace 3 with the correct column index for the 'color' field
                        'boolean': row[9],  # Replace 4 with the correct column index for the 'boolean' field
                        'amount': int(row[10]),  # Replace 5 with the correct column index for the 'amount' field
                        'notes': row[11],  # R
                        'partner_name': partner_name,
                    })

                    # Add stock move for the picked product
                    move_vals = {
                        'name': product.name,
                        'product_id': product.id,
                        'product_uom_qty': product_qty,
                        'product_uom': uom.id,  # Set the product UoM here
                        'picking_id': picking.id,
                        'location_id': source_location.id,
                        'location_dest_id': dest_location.id,
                    }
                    self.env['stock.move'].create(move_vals)

            except xlrd.XLRDError:
                raise UserError(_('Cannot determine the file format for the attached file.'))

        else:
            raise UserError(_('Invalid file type selected. Please select either CSV or XLS file.'))

    def download_excel_button(self):
        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Sheet')
        s_h = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour yellow; align: horiz center")

        # Write field names as headers in the first row
        field_names = ['NAME', 'CUSTOMER', 'SOURCE DOCUMENT', 'DATE', 'PRODUCT', 'QUANTITY', 'LOT', 'UOM', 'COLOR', 'BOOLEAN', 'AMOUNT', 'NOTES']
        for col, field_name in enumerate(field_names):
            ws.write(0, col, field_name, s_h)

        # Retrieve inventory data or adapt this query based on your requirement
        inventory_data = self.env['stock.picking'].search([])

        if inventory_data:
            row = 1
            for line in inventory_data:
                ws.write(row, 0, line.name)
                ws.write(row, 1, line.partner_id.name)
                ws.write(row, 2, line.origin)
                ws.write(row, 3, line.date.strftime('%Y-%m-%d %H:%M:%S'))
                ws.write(row, 4, line.product_id.name)

                # Add stock move for the picked product
                for move_line in line.move_line_ids_without_package:
                    ws.write(row, 5, move_line.product_uom_qty)
                    ws.write(row, 6, move_line.lot_id.name)
                    ws.write(row, 7, move_line.product_uom_id.name)
                    ws.write(row, 8, line.color)
                    ws.write(row, 9, line.boolean)
                    ws.write(row, 10, line.amount)
                    ws.write(row, 11, line.notes)
                    row += 1

                # Increment the row to start writing on the next row for the next 'line' record
                row += 1

        else:
            raise UserError(_("Currently, there is no inventory data!"))

        filename = 'Inventory.xls'
        workbook.save(filename)
        with open(filename, "rb") as file:
            file_data = file.read()
        out = base64.encodebytes(file_data)
        self.write({'filename': filename, 'file': out, 'flag': True})

        return {
            'type': 'ir.actions.act_url',
            'url': "data:application/vnd.ms-excel;base64," + out.decode('utf-8'),
            'target': 'new',
            'filename': filename,
        }

    def download_csv_button(self):
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Write field names as headers in the first row
        csv_header = ['NAME', 'CUSTOMER', 'SOURCE DOCUMENT', 'DATE', 'PRODUCT', 'QUANTITY', 'LOT', 'UOM', 'COLOR',
                      'BOOLEAN', 'AMOUNT', 'NOTES']
        csv_writer.writerow(csv_header)

        # Retrieve inventory data or adapt this query based on your requirement
        inventory_data = self.env['stock.picking'].search([])  # Get all inventory records

        if inventory_data:
            for line in inventory_data:
                row = [
                    line.name,
                    line.partner_id.name,
                    line.origin,
                    line.date.strftime('%Y-%m-%d %H:%M:%S') if line.date else '',
                    line.product_id.name,
                ]

                # Add stock move for the picked product
                for move_line in line.move_line_ids_without_package:
                    row.extend([move_line.product_uom_qty, move_line.lot_id.name, move_line.product_uom_id.name])
                    # row.append(line.partner_name)
                    row.append(line.color)
                    row.append(line.boolean)
                    row.append(line.amount)
                    row.append(line.notes)
                    csv_writer.writerow(row[:])  # Create a copy of the list to avoid modifying the same row

        else:
            raise UserError(_("Currently, there is no inventory data!"))

        csv_data = csv_buffer.getvalue()
        csv_buffer.close()

        csv_file_name = 'inventory.csv'
        return {
            'type': 'ir.actions.act_url',
            'url': "data:text/csv;charset=utf-8," + csv_data,
            'target': 'new',
            'filename': csv_file_name,
        }