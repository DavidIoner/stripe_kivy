from calendar import c
import components.DButilC as dbutil
from weasyprint import HTML
import os
from jinja2 import Environment, FileSystemLoader
import requests
from datetime import datetime
from components.send_pdf import send_email


def get_rate(id="MXN-BRL"):
    url = "https://economia.awesomeapi.com.br/last/" + id
    response = requests.get(url)
    data = response.json()
    data_id = id.replace("-", "")
    rate = data[data_id]["bid"]
    return float(rate)


class Report:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.ROOT = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_SRC = os.path.join(self.ROOT, 'templates')
        self.DEST_DIR = os.path.join(self.ROOT, 'output')

    def create_customer(self, template_file):
        print('start generate report...')
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_SRC))
        template = env.get_template(template_file)
        css = os.path.join(self.TEMPLATE_SRC, 'styles.css')
        customer_row = dbutil.get_row(self.customer_id)
        print('setting variables')
        # variables
        BRL = get_rate('BRL-USD')
        MXN = get_rate('MXN-USD')
        COP = get_rate('COP-USD')
        MXNU = 1 / MXN
        BRLU = 1 / BRL
        COPU = 1 / COP
        ###### DEFINE LOCAL ######
        local = 1
        specific_location = ''
        ###### DEFINE CLAUSE 21 ######
        if customer_row[10] != '0' or customer_row[10] is not None:
            clause21_p = f'21. Apartment Rental: Should the licensee elect to pay for the service, 5CRE will provide non-exclusive use of a two-bedroom apartment in {city} for ${customer_row[10]} USD per year, payable as one lump sum at signing. 5CRE shall provide cleaning before and after their stay. Bedding, towels, and toiletries can be provided at an extra charge. All bookings are made on a first-come, first-serve basis. The customer is guaranteed three nights per month. Customer may extend their stay, free of charge, or elect to stay multiple times in any one-month period on the condition that it is not already booked by another customer. No stay may exceed ten days. 5CRE retains the right to refund a proportionate share of the annual payment and terminate staying rights for any reason. Included cleaning is limited to reasonable stay wear and tear. Apartment sharing agreement shall expire one year from payment. <br> <br>'
        else:
            clause21_p = ''


        vars_dict = {
            "date": datetime.now().strftime("%d/%m/%Y"),
            "local": local,
            "specific_location": specific_location,
            "customer": customer_row[1],
            "company": customer_row[2],
            "located_at": customer_row[3],
            "phone": customer_row[4],
            "email": customer_row[5],
            "licensor": customer_row[6],
            "onboard": customer_row[8],
            "apartment": customer_row[9],
            "security": customer_row[10],
            "clause21_p": clause21_p,
        }
        vars_dict.update({'MXN': f'{MXN:.2f}', 'BRL': f'{BRL:.2f}', 'COP': f'{COP:.2f}', 'MXNU': f'{MXNU:.2f}', 'BRLU': f'{BRLU:.2f}', 'COPU': f'{COPU:.2f}'})
        
        print('rendering')
        output_name = f'{customer_row[1]}_base.pdf'
        # rendering to html string
        vars_dict['template_src'] = 'file://' + self.TEMPLATE_SRC
        rendered_string = template.render(vars_dict)
        html = HTML(string=rendered_string)
        report = os.path.join(self.DEST_DIR, output_name)
        print('generating pdf')
        html.write_pdf(report, stylesheets=[css])
        print(f'base file is generated successfully and under {self.DEST_DIR}')

    def create_worker(self, template_file):
        pass
#
    def merge_pdf(self, output_name):
        pass