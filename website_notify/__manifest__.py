{
    "name" : "Website Stock Notify",
    "version" : "14.0",
    "depends" : ['product','sale','delivery','base','stock','sale_stock','website','website_sale'],
    "author" : "Redian Software",
    "description": """Website Management""",
    "website" : "https://www.rediansoftware.com/",
    "category" : "Website Management",
    'summary': 'Display website stock email notification on website',
    'currency': 'USD',
    'price': '27.0',
    "sequence": -109,
    "demo" : [],
    "data" : [
        "security/ir.model.access.csv",
        "data/email_notify.xml",
        "views/email_notification_view.xml",
        "views/email_template_notify.xml",
    ],
    'auto_install': False,
    "installable": True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

