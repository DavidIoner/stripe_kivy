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

        self.customer_row = dbutil.get_row(self.customer_id)
        self.currency = self.customer_row[11]

        self.BRL = get_rate('BRL-USD')
        self.MXN = get_rate('MXN-USD')
        self.COP = get_rate('COP-USD')
        self.MXNU = 1 / self.MXN
        self.BRLU = 1 / self.BRL
        self.COPU = 1 / self.COP

    def create_customer(self):
        print('start generate report...')
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_SRC))
        template = env.get_template('CRE_contract.html')
        css = os.path.join(self.TEMPLATE_SRC, 'styles.css')
        vars_dict = {}
        print('setting variables')
        # variables

        ###### DEFINE LOCAL ######
        local = 1
        specific_location = ''
        ###### DEFINE CLAUSE 21 ######
        if self.customer_row[10] != '0' or self.customer_row[10] is not None:
            # definir o local!!
            city = 'cidade'
            clause21_p = f'21. Apartment Rental: Should the licensee elect to pay for the service, 5CRE will provide non-exclusive use of a two-bedroom apartment in {city} for ${self.customer_row[10]} USD per year, payable as one lump sum at signing. 5CRE shall provide cleaning before and after their stay. Bedding, towels, and toiletries can be provided at an extra charge. All bookings are made on a first-come, first-serve basis. The customer is guaranteed three nights per month. Customer may extend their stay, free of charge, or elect to stay multiple times in any one-month period on the condition that it is not already booked by another customer. No stay may exceed ten days. 5CRE retains the right to refund a proportionate share of the annual payment and terminate staying rights for any reason. Included cleaning is limited to reasonable stay wear and tear. Apartment sharing agreement shall expire one year from payment. <br> <br>'
            vars_dict.update({"clause21_p": clause21_p})


        vars_dict.update({
            "date": datetime.now().strftime("%d/%m/%Y"),
            "local": local,
            "specific_location": specific_location,
            "customer": self.customer_row[1],
            "company": self.customer_row[2],
            "located_at": self.customer_row[3],
            "phone": self.customer_row[4],
            "email": self.customer_row[5],
            "licensor": self.customer_row[6],
            "onboard": self.customer_row[8],
            "apartment": self.customer_row[9],
        })
        vars_dict.update({'MXN': f'{self.MXN:.2f}', 'BRL': f'{self.BRL:.2f}', 'COP': f'{self.COP:.2f}', 'MXNU': f'{self.MXNU:.2f}', 'BRLU': f'{self.BRLU:.2f}', 'COPU': f'{self.COPU:.2f}'})
        
        print('rendering customer template')
        output_name = f'{self.customer_row[1]}_base.pdf'
        # rendering to html string
        vars_dict['template_src'] = 'file://' + self.TEMPLATE_SRC
        rendered_string = template.render(vars_dict)
        html = HTML(string=rendered_string)
        report = os.path.join(self.DEST_DIR, output_name)
        print('generating pdf')
        html.write_pdf(report, stylesheets=[css])
        print(f'base file is generated successfully and under {self.DEST_DIR}')
        return report

    def create_worker(self, worker_id, exibith):
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_SRC))
        template = env.get_template('CRE_contract_exibith.html')
        css = os.path.join(self.TEMPLATE_SRC, 'styles.css')
        worker_row = dbutil.get_row(worker_id, table="workers")
        print(worker_row)
        vars_dict = {}

        # variables
        if worker_row[6] == "1":
            print('holiday actived!')
            ## conferir se eh mxn ou mxnu
            if self.currency == 'USD':
                holiday = float(worker_row[3]) * 12 * 0.023 * self.MXN
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${holiday:.2f} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p}) 
                print("currency is USD")  
            if self.currency.upper == 'MXN':
                holiday = float(worker_row[3]) * 12 * 0.023 
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${holiday:.2f} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p})      

        if worker_row[4] is not None:
            christmas_p = f'<strong>Christmas Bonus</strong> $ MXN ($ USD at time of writing, subject to change), payable for all workers who have been working at your organization for 4 or more months. Charged by 5CRE’s LATAM affiliate. Payable On December 1. <br> <br>'
            vars_dict.update({'christmas_p': christmas_p})        
            print(vars_dict)  
        

        if self.currency == 'USD':
            desk_fee_usd = worker_row[4]
            affiliate = "5CRE’s affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})
        elif self.currency == 'MXN':
            ## ver se esta certo
            desk_fee_usd = worker_row[4] / self.MXN
            affiliate = "5CRE’s LATAM affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})

            
        biwage = float(worker_row[3]) / 2

        vars_dict.update({
            "currency": self.currency,
            "exibith": exibith,
            "biwage": biwage,
            "worker": worker_row[1],
            "wage": worker_row[3],
            "desk": worker_row[4],     
        })

        output_name = f'{self.customer_row[1]}_exibith_{exibith}.pdf'
        # rendering to html string
        vars_dict['template_src'] = 'file://' + self.TEMPLATE_SRC
        rendered_string = template.render(vars_dict)
        html = HTML(string=rendered_string)
        report = os.path.join(self.DEST_DIR, output_name)
        print('generating pdf')
        html.write_pdf(report, stylesheets=[css])
        print(f'base file is generated successfully and under {self.DEST_DIR}')
        return report




#
    def merge_pdf(self, output_name):
        pass