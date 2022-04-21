import components.DButilC as dbutil
from weasyprint import HTML
import os
from jinja2 import Environment, FileSystemLoader
import requests
from datetime import datetime
from components.send_pdf import send_email, get_settings
from PyPDF2 import PdfFileMerger


def get_rate(id="MXN-BRL"):
    url = "https://economia.awesomeapi.com.br/last/" + id
    response = requests.get(url)
    data = response.json()
    data_id = id.replace("-", "")
    rate = data[data_id]["bid"]
    return float(rate)

def monetary(money, dot=True):
    money = str(money)
    if "." in money:
        money = money.split(".")
        if len(money[1]) == 1:
            money[1] = money[1] + "0"
        if dot:
            money = money[0] + "." + money[1][-2:]
        if dot == False:
            money = money[0] + money[1][-2:]
    else:
        money = money[:-2] + "." + money[-2:]
    return money


class Report:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.ROOT = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_SRC = os.path.join(self.ROOT, 'templates')
        self.DEST_DIR = os.path.join(self.ROOT, 'output')


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


        # customer variables
        self.customer_row = dbutil.get_row(self.customer_id)
        self.customer_name = self.customer_row[1]
        customer_company = self.customer_row[2]
        customer_located_at = self.customer_row[3]
        customer_phone = self.customer_row[4]
        customer_email = self.customer_row[5]
        customer_licensor = self.customer_row[6]
        customer_local = self.customer_row[7]
        self.currency = self.customer_row[8]
        self.currency = str(self.currency).upper()
        self.customer_christmas = self.customer_row[9]
        # customer_stripe_id = self.customer_row[12]

        ###### DEFINE LOCAL ######
        local_row = dbutil.get_row(customer_local, table="locals")
        local_city = local_row[1]
        local_contry = local_row[2]
        local_specific = local_row[3]

        ###### DEFINE CLAUSE 21 ######
        apartment_price = 0
        for worker in dbutil.get_all("workers"):
            worker_customer = worker[1]
            worker_apartment = worker[5]
            if worker_customer == self.customer_name and worker_apartment != 0 and worker_apartment is not None:
                apartment_price += worker_apartment
                
        if apartment_price != 0:
            clause21_p = f'21. Apartment Rental: Should the licensee elect to pay for the service, 5CRE will provide non-exclusive use of a two-bedroom apartment in {local_city} for ${monetary(apartment_price)} {self.currency} per year, payable as one lump sum at signing. 5CRE shall provide cleaning before and after their stay. Bedding, towels, and toiletries can be provided at an extra charge. All bookings are made on a first-come, first-serve basis. The customer is guaranteed three nights per month. Customer may extend their stay, free of charge, or elect to stay multiple times in any one-month period on the condition that it is not already booked by another customer. No stay may exceed ten days. 5CRE retains the right to refund a proportionate share of the annual payment and terminate staying rights for any reason. Included cleaning is limited to reasonable stay wear and tear. Apartment sharing agreement shall expire one year from payment. <br> <br>'
            vars_dict.update({"clause21_p": clause21_p})



        vars_dict.update({
            "date": datetime.now().strftime("%d/%m/%Y"),
            "city": local_city,
            "country": local_contry,
            "specific_location": local_specific,
            "customer": self.customer_name,
            "company": customer_company,
            "located_at": customer_located_at,
            "phone": customer_phone,
            "email": customer_email,
            "licensor": customer_licensor,
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
        vars_dict = {}

        # variables
        worker_name = worker_row[2]
        worker_wage = worker_row[3]
        worker_desk = worker_row[4]
        # worker_apartment = worker_row[5]
        worker_onboard = worker_row[6]
        worker_holiday = worker_row[7]
        worker_currency_wage = worker_row[8]
        worker_currency_wage = str(worker_currency_wage).upper()

        if worker_currency_wage == "MXN":
            wage = float(monetary(worker_wage)) * self.MXN
            wage = int(monetary(wage, dot=False))
        security = (wage + worker_desk) * 2
        ## conferir se esta fora de escopo
        security = monetary(security)
        vars_dict.update({"security": security})

        if "1" in worker_holiday:
            print('holiday actived!')
            ## conferir se eh mxn ou mxnu
            if self.currency == 'USD':
                ## holiday * 24 * 0.023
                holiday = float(monetary(worker_wage)) * 0.552 * self.MXN
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${monetary(holiday)} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p})
            if self.currency == 'MXN':
                holiday = float(monetary(worker_wage)) * 0.552 
                holiday_p = f'<strong>Federal Holiday Fee</strong> ${monetary(holiday)} {self.currency}, herein 2.3% of annual compensation to remove federal holidays from work days. <br> <br>'
                vars_dict.update({"holiday_p": holiday_p})     

        ## conferir currency wage, se for em usd a logica muda
        if "1" in self.customer_christmas:
            amount = worker_wage + int(worker_wage / 14)
            christmas_usd = float(monetary(amount)) * self.MXN
            christmas_p = f'<strong>Christmas Bonus</strong> ${monetary(amount)} MXN ($ {monetary(christmas_usd)} USD at time of writing, subject to change), payable for all workers who have been working at your organization for 4 or more months. Charged by 5CRE’s LATAM affiliate. Payable On December 1. <br> <br>'
            vars_dict.update({'christmas_p': christmas_p})        

        

        if self.currency == 'USD':
            desk_fee_usd = monetary(worker_desk)
            affiliate = "5CRE’s affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})
        elif self.currency == 'MXN':
            ## ver se esta certo
            desk_fee_usd = monetary(float(monetary(worker_desk)) / self.MXN)
            affiliate = "5CRE’s LATAM affiliate."
            vars_dict.update({"desk_fee_USD": desk_fee_usd, "affiliate": affiliate})

        if worker_currency_wage == "USD":
            wage_usd = monetary(worker_wage)
            wage = monetary(float(wage_usd) / self.MXN)
            affiliate_wage = "5CRE’s affiliate."
            vars_dict.update({"wage_usd": wage_usd, "affiliate_wage": affiliate_wage, "wage": wage, "currency_wage": worker_currency_wage})
        else:
            wage = monetary(worker_wage)
            wage_usd = monetary(float(wage) * self.MXN)
            affiliate_wage = "5CRE’s LATAM affiliate."
            vars_dict.update({"wage_usd": wage_usd, "affiliate_wage": affiliate_wage, "wage": wage, "currency_wage": worker_currency_wage})

            


        vars_dict.update({
            "currency": self.currency,
            "exibith": exibith,
            "worker": worker_name,
            "onboard": monetary(worker_onboard),
            #"wage": monetary(worker_row[3]), ## deve ter em mxn tambem
            "desk": monetary(worker_desk),   
        })

        output_name = f'{self.customer_name}_exibith_{exibith}.pdf'
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

    output_folder = get_settings("output_folder")
    output = f"{output_folder}/{output_name}.pdf"
    merger.write(output)
    merger.close()

    return output


def delete_temp_files():
    for file in os.listdir("./components/output"):
        if "base" in file:
            os.remove(os.path.join("./components/output", file))
        if "exibith" in file:
            os.remove(os.path.join("./components/output", file))
        

