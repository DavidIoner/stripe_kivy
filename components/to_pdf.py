import components.DButilC as dbutil
from weasyprint import HTML
import os
from jinja2 import Environment, FileSystemLoader
import requests
from datetime import datetime
from components.send_pdf import send_email
from PyPDF2 import PdfFileMerger


def get_rate(id="MXN-BRL"):
    url = "https://economia.awesomeapi.com.br/last/" + id
    response = requests.get(url)
    data = response.json()
    data_id = id.replace("-", "")
    rate = data[data_id]["bid"]
    return float(rate)

def monetary(money):
    money = str(money)
    if "." in money:
        money = money.split(".")
        print(money[1])
        money = money[0] + "." + money[1][-2:]
    else:
        money = money[:-2] + "." + money[-2:]
    return money


class Report:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.ROOT = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_SRC = os.path.join(self.ROOT, 'templates')
        self.DEST_DIR = os.path.join(self.ROOT, 'output')

        self.customer_row = dbutil.get_row(self.customer_id)
        self.currency = self.customer_row[10]

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
        local_row = dbutil.get_row(self.customer_row[7], table="locals")
        ###### DEFINE CLAUSE 21 ######
        if self.customer_row[9] != '0' or self.customer_row[9] is not None:
            clause21_p = f'21. Apartment Rental: Should the licensee elect to pay for the service, 5CRE will provide non-exclusive use of a two-bedroom apartment in {local_row[1]} for ${monetary(self.customer_row[9])} {self.currency} per year, payable as one lump sum at signing. 5CRE shall provide cleaning before and after their stay. Bedding, towels, and toiletries can be provided at an extra charge. All bookings are made on a first-come, first-serve basis. The customer is guaranteed three nights per month. Customer may extend their stay, free of charge, or elect to stay multiple times in any one-month period on the condition that it is not already booked by another customer. No stay may exceed ten days. 5CRE retains the right to refund a proportionate share of the annual payment and terminate staying rights for any reason. Included cleaning is limited to reasonable stay wear and tear. Apartment sharing agreement shall expire one year from payment. <br> <br>'
            vars_dict.update({"clause21_p": clause21_p})



        vars_dict.update({
            "date": datetime.now().strftime("%d/%m/%Y"),
            "city": local_row[1],
            "country": local_row[2],
            "specific_location": local_row[3],
            "customer": self.customer_row[1],
            "company": self.customer_row[2],
            "located_at": self.customer_row[3],
            "phone": self.customer_row[4],
            "email": self.customer_row[5],
            "licensor": self.customer_row[6],
            "onboard": monetary(self.customer_row[8]),
            "apartment": monetary(self.customer_row[9]),
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
        if "1" in worker_row[6]:
            print('holiday actived!')
            ## conferir se eh mxn ou mxnu
            print(self.currency)
            if self.currency == 'usd':
                holiday = float(monetary(worker_row[3])) * 0.276 * self.MXN
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${holiday:.2f} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p}) 
                print(holiday_p)    
            if self.currency == 'mxn':
                holiday = float(monetary(worker_row[3])) * 0.276 
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${holiday:.2f} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p})
                print(holiday_p)      

        if worker_row[4] is not None:
            christmas_usd = monetary(float(monetary(worker_row[4])) * self.MXN)
            christmas_p = f'<strong>Christmas Bonus</strong> ${monetary(worker_row[4])}MXN ($ {christmas_usd} USD at time of writing, subject to change), payable for all workers who have been working at your organization for 4 or more months. Charged by 5CRE’s LATAM affiliate. Payable On December 1. <br> <br>'
            vars_dict.update({'christmas_p': christmas_p})        

        

        if self.currency == 'usd':
            desk_fee_usd = monetary(worker_row[5])
            affiliate = "5CRE’s affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})
        elif self.currency == 'mxn':
            ## ver se esta certo
            desk_fee_usd = float(monetary(worker_row[5])) / self.MXN
            desk_fee_usd = f'{desk_fee_usd:.2f}'
            affiliate = "5CRE’s LATAM affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})

        if worker_row[7] == "usd":
            wage_usd = monetary(worker_row[3])
            wage = monetary(float(wage_usd) / self.MXN)
            affiliate_wage = "5CRE’s affiliate."
            vars_dict.update({"wage_usd": wage_usd, "affiliate_wage": affiliate_wage, "wage": wage, "currency_wage": worker_row[7]})
        else:
            wage = monetary(worker_row[3])
            wage_usd = monetary(float(wage) * self.MXN)
            affiliate_wage = "5CRE’s LATAM affiliate."
            vars_dict.update({"wage_usd": wage_usd, "affiliate_wage": affiliate_wage, "wage": wage, "currency_wage": worker_row[7]})

            
        wagex2 = monetary(worker_row[3] * 2)

        vars_dict.update({
            "currency": self.currency,
            "exibith": exibith,
            "wagex2": wagex2,
            "worker": worker_row[2],
            #"wage": monetary(worker_row[3]), ## deve ter em mxn tambem
            "desk": monetary(worker_row[5]),   
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
def merge_pdf(pdf_list, output_name):
    merger = PdfFileMerger()

    for pdf in pdf_list:
        merger.append(pdf)

    merger.write(f"components/output/{output_name}.pdf")
    merger.close()


def delete_temp_files():
    for file in os.listdir("./components/output"):
        if "base" in file:
            os.remove(os.path.join("./components/output", file))
        if "exibith" in file:
            os.remove(os.path.join("./components/output", file))
        
