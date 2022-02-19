from weasyprint import HTML
import os
from jinja2 import Environment, FileSystemLoader
import requests
from datetime import datetime
from components.send_pdf import send_email

# come back one directory
def get_rate(id="MXN-BRL"):
    url = "https://economia.awesomeapi.com.br/last/" + id
    response = requests.get(url)
    data = response.json()
    data_id = id.replace("-", "")
    rate = data[data_id]["bid"]
    return float(rate)

class Report:
    def __init__(self, vars_dict={}):
        self.vars_dict = vars_dict
        self.ROOT = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_SRC = os.path.join(self.ROOT, 'templates')
        self.DEST_DIR = os.path.join(self.ROOT, 'output')
       

    def start(self, template_file, output_name=False):
        print('start generate report...')
        env = Environment(loader=FileSystemLoader(self.TEMPLATE_SRC))
        template = env.get_template(template_file)
        css = os.path.join(self.TEMPLATE_SRC, 'styles.css')
        
        print('setting variables')
        # variables
        BRL = get_rate('BRL-USD')
        MXN = get_rate('MXN-USD')
        COP = get_rate('COP-USD')
        MXNU = 1 / MXN
        BRLU = 1 / BRL
        COPU = 1 / COP
        if 'USD' in self.vars_dict['security']:
            security_temp = self.vars_dict['security'].replace('USD', '')
            security_cash = float(security_temp)
            security_coin = 'USD'
            affiliate_security = '5CRE'
        else:
            security_temp = self.vars_dict['security'].replace('MXN', '')
            security_cash = float(security_temp)
            security_coin = 'MXN'
            affiliate_security = '5CRE’s LATAM affiliate'
        if 'USD' in self.vars_dict['onboard']:
            onboard_temp = self.vars_dict['onboard'].replace('USD', '')
            onboard_cash = float(onboard_temp)
            onboard_coin = 'USD'
            affiliate_onboard = '5CRE'
        else:
            onboard_temp = self.vars_dict['onboard'].replace('MXN', '')
            onboard_cash = float(onboard_temp)
            onboard_coin = 'MXN'
            affiliate_onboard = '5CRE’s LATAM affiliate'
        if 'USD' in self.vars_dict['apartment']:
            apartment_temp = self.vars_dict['apartment'].replace('USD', '')
            if apartment_temp != '' or apartment_temp != '0':
                apartment_cash = float(apartment_temp)
                apartment_price_USD = apartment_cash
                apartment_coin = 'USD'
                affiliate_apartment = '5CRE'
        else:
            apartment_temp = self.vars_dict['apartment'].replace('MXN', '')
            if apartment_temp != '' or apartment_temp == '0':
                apartment_cash = float(apartment_temp)
                apartment_price_USD = apartment_cash * MXN
                apartment_coin = 'MXN'
                affiliate_apartment = '5CRE’s LATAM affiliate'
             
        if apartment_temp == '' or apartment_temp == '0':
            apartment_p = ''
            clause21_p = ''       
        else: 
            city = self.vars_dict['city']    
            apartment_price_USD_year = apartment_price_USD * 12    
            clause21_p = f'21. Apartment Rental: Should the licensee elect to pay for the service, 5CRE will provide non-exclusive use of a two-bedroom apartment in {city} for ${apartment_price_USD_year} USD per year, payable as one lump sum at signing. 5CRE shall provide cleaning before and after their stay. Bedding, towels, and toiletries can be provided at an extra charge. All bookings are made on a first-come, first-serve basis. The customer is guaranteed three nights per month. Customer may extend their stay, free of charge, or elect to stay multiple times in any one-month period on the condition that it is not already booked by another customer. No stay may exceed ten days. 5CRE retains the right to refund a proportionate share of the annual payment and terminate staying rights for any reason. Included cleaning is limited to reasonable stay wear and tear. Apartment sharing agreement shall expire one year from payment. <br> <br>'
            apartment_p = f'<strong>Apartment Fee:</strong> ${apartment_cash} {apartment_coin}, Charged by {affiliate_apartment}. <br>'

        print('stage 1')
        wage_USD = float(self.vars_dict['wage_MXN']) * MXN
        christmas_USD = float(self.vars_dict['christmas_MXN']) * MXN

        biwage = float(self.vars_dict['wage_MXN']) / 2
        biwage_USD = biwage * MXN
        if self.vars_dict['holiday_fee']:
            if self.vars_dict['holiday_coin'] == 'USD':
                holiday_cash = float(self.vars_dict['wage_MXN']) * 12 * 0.023 * MXN
            if self.vars_dict['holiday_coin'] == 'MXN':
                holiday_cash = float(self.vars_dict['wage_MXN']) * 12 * 0.023 
            holiday_coin = self.vars_dict['holiday_coin']
            holiday_p = f'<strong>Federal Holiday Fee</strong> ${holiday_cash:.2f} {holiday_coin}, herein 2.3% of annual compensation to remove federal holidays from work days.'
        else:
            holiday_p = ''
        
        # setting variables into the template
        self.vars_dict.update({'date': datetime.now().strftime('%d/%m/%Y')})
        self.vars_dict.update({'MXN': f'{MXN:.2f}', 'BRL': f'{BRL:.2f}', 'COP': f'{COP:.2f}', 'MXNU': f'{MXNU:.2f}', 'BRLU': f'{BRLU:.2f}', 'COPU': f'{COPU:.2f}'})
        self.vars_dict.update({ 
        'apartment_p': apartment_p, 
        'clause21_p': clause21_p,
        'security_affiliate': affiliate_security, 
        'security_cash': f'{security_cash:.2f}', 
        'security_coin': security_coin, 
        'onboard_affiliate': affiliate_onboard, 
        'onboard_coin': onboard_coin,
        'onboard_cash': f'{onboard_cash:.2f}', 
        'wage_USD': f'{wage_USD:.2f}', 
        'biwage': f'{biwage:.2f}',
        'biwage_USD': f'{biwage_USD:.2f}', 
        'christmas_USD': f'{christmas_USD:.2f}',  
        'holiday_p': holiday_p})

        print('rendering')
        # rendering to html string
        self.vars_dict['template_src'] = 'file://' + self.TEMPLATE_SRC
        rendered_string = template.render(self.vars_dict)
        html = HTML(string=rendered_string)
        report = os.path.join(self.DEST_DIR, output_name)
        print('generating pdf')
        html.write_pdf(report, stylesheets=[css])
        print(f'file is generated successfully and under {self.DEST_DIR}')
        print('sending email')
        send_email(report)
        
 



