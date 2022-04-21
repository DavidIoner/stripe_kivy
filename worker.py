from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
import components.to_pdf as pdf
import components.DButilC as dbutil
import components.payment as payment
import components.send_pdf as send_pdf
import tkinter as tk
from tkinter import filedialog
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
import json

def askdirectory():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory()


class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("components/worker_ui.kv")

        # to avoid bugs
        self.holiday_check = False
        self.customer_row = None
        self.currency_wage = False

        self.data = {
            "output folder": "components/icons/outputfolder.png",
            "email": "components/icons/email.png",
        }        
        speed_dial = MDFloatingActionButtonSpeedDial()
        speed_dial.data = self.data
        speed_dial.root_button_anim = True
        speed_dial.callback = self.settings
        self.kv.add_widget(speed_dial)


        menu_items_customer = [
            {
                "viewclass": "OneLineIconListItem",
                "text": customer[1],
                "height": dp(56),
                "on_release": lambda x=customer[0]: self.set_customer(x)}
            
            for customer in dbutil.get_all()
        ]


        self.customer_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_customer,
            items=menu_items_customer,
            position="bottom",
            width_mult=4,
        )

    def set_customer(self, customer_id):
        self.customer_row = dbutil.get_row(customer_id)
        self.customer_id = self.customer_row[0]
        self.customer_name = self.customer_row[1]
        self.customer_email = self.customer_row[5]
        self.customer_currency = self.customer_row[8]
        self.customer_christmas = self.customer_row[9]
        self.customer_stripe_id = self.customer_row[10]

        # confere o tipo de pagamento
        if self.customer_stripe_id is not None:
            cus = payment.retrieve_customer(self.customer_stripe_id)
            if cus.default_source is not None:
                src = payment.retrieve_source(cus.default_source)
                self.customer_source_type = src.type
                print(f"Payment method: {self.customer_source_type}")
                if self.customer_source_type == "card":
                    print("4% will be added")

        else:
            print("this customer has no stripe id!!!")
            print("Not avaliable to charge")
       
        self.kv.ids.drop_customer.set_item(self.customer_name)
        self.customer_menu.dismiss()

        if self.customer_currency == "usd":
            self.root.ids.onboard.hint_text = "Onboard (USD)"
        elif self.customer_currency == "mxn":
            self.root.ids.onboard.hint_text = "Onboard (MXN)"

        ## mostrar a lista dos workers desse customer (pelo menos o nome e a qtd em um menu)
    def settings(self, instance):
        if instance.icon == "components/icons/outputfolder.png":
            directory = askdirectory()
            # open settings.json and write the new directory
            with open("components/settings.json", "r") as f:
                settings = json.load(f)
                settings["output_folder"] = directory
            with open("components/settings.json", "w") as f:
                json.dump(settings, f)
        if instance.icon == "components/icons/email.png":
            print("not avaliable yet")

    def check_wage_currency(self, checkbox, active):
        if active:
            self.currency_wage = True
            self.root.ids.wage.hint_text = "bi-weekly wage (USD)"
        else:
            self.currency_wage = False
            self.root.ids.wage.hint_text = "bi-weekly wage (MXN)"

    def check_holiday(self, checkbox, active):
        if active:
            self.holiday_check = True
            self.root.ids.holiday_label.text = "Holiday fee active!"

        if not active:
            self.holiday_check = False
            self.root.ids.holiday_label.text = "Holiday fee deactive!"

    def submit(self):
        name = self.root.ids.worker.text
        
        for worker in dbutil.get_all("workers"):
            if worker[2] == name and worker[1] == self.customer_name:
                print("worker already exists!")
                return

        item_dict = {}
        if self.customer_row is not None:
            if self.holiday_check:
                self.holiday = "1"
                item_dict.update({"holiday": self.holiday})
            else:
                self.holiday = "0"
                item_dict.update({"holiday": self.holiday})

            if self.currency_wage == True:
                currency_wage = "usd"
                item_dict.update({"currency_wage": currency_wage})
            else:
                currency_wage = "mxn"
                item_dict.update({"currency_wage": currency_wage})
            


            item_dict.update({
                "customer": self.customer_name,
                "name": name,
                "wage": self.root.ids.wage.text,
                "desk": self.root.ids.desk.text,
                "onboard": self.root.ids.onboard.text,
                "apartment": self.root.ids.apartment.text,
                "holiday": self.holiday,
            })

            # add to database
            dbutil.insert_data_worker(item_dict)

        else:
            print("customer not selected")
        # add to dropdowns

    def generate_pdf(self):
        # GENERATE CUSTOMER PART #
        gen_pdf = pdf.Report(self.customer_id)
        customer = gen_pdf.create_customer()
        pdf_list = [customer]
        # GENERATE WORKER PART #
        exibith = 0
        for worker in dbutil.get_all("workers"):
            worker_row = dbutil.get_row(worker[0], table="workers")
            if worker_row[1] == self.customer_name:
                exibith += 1
                worker = gen_pdf.create_worker(worker_row[0], exibith)
                pdf_list.append(worker)


        file = pdf.merge_pdf(pdf_list, self.customer_name)
        print(file)
        pdf.delete_temp_files()
        send_pdf.send_email(file)


    ## criar as subscriptions e charges correspondentes
    def submit_payments(self):
        MXN = pdf.get_rate('MXN-USD')
        # confere se o customer tem um stripe_id
        if self.customer_stripe_id is None:
            print("customer has no stripe id")
            return
         
        total_charge = 0
        charges = {}

        # subscriptions and worker prices
        for worker in dbutil.get_all("workers"):
            worker_customer = worker[1]
            # confere a relacao do worker com o customer
            holiday = 0
            if worker_customer == self.customer_name:
                worker_name = worker[2]
                worker_wage = worker[3]
                worker_desk = worker[4]
                worker_apartment = worker[5]
                worker_onboard = worker[6]
                worker_holiday = worker[7]
                worker_currency_wage = worker[8]
                worker_desk_id = worker[9]
                worker_wage_id = worker[10]
                worker_christmas_id = worker[11]



                if worker_apartment != "0" and worker_apartment != "" and worker_apartment is not None:
                    if self.customer_source_type == "card":
                        worker_apartment = float(pdf.monetary(worker_apartment)) * 1.04
                        worker_apartment = pdf.monetary(worker_apartment, dot=False)
                    total_charge += int(worker_apartment)
                    charges.append(f"{worker_name} apartment = {pdf.monetary(worker_apartment)}")
                    charges.update({f"{worker_name} apartment": f"{pdf.monetary(worker_apartment)}"})
                    #apartment_charge = payment.create_charge(self.customer_stripe_id, worker_apartment, self.customer_currency, f"{worker_name}'s apartment")
                    #print(f"apartment charge id for {worker_name}: {apartment_charge.id}")

                if "1" in worker_holiday:
                    ## conferir se eh mxn ou mxnu
                    if self.customer_currency == 'usd':
                        holiday = float(pdf.monetary(worker_wage)) * 0.552 * MXN
                    if self.customer_currency == 'mxn':
                        holiday = float(pdf.monetary(worker_wage)) * 0.552
                    holiday = int(pdf.monetary(holiday, dot=False))

                    if self.customer_source_type == "card":
                        holiday = float(pdf.monetary(holiday)) * 1.04
                        holiday = int(pdf.monetary(holiday, dot=False))
                    total_charge += int(holiday)
                    charges.update({f"{worker_name} holiday": f"{pdf.monetary(holiday)}"})
                    # holiday_charge = payment.create_charge(self.customer_stripe_id, holiday, self.customer_currency, f"{worker_name}'s holiday compensation")
                    # print(f"holiday charge id for {worker_name}: {holiday_charge.id}")


                # create security charge
                if worker_currency_wage == "usd":
                    security = (worker_wage + worker_desk) * 2
                if worker_currency_wage == "mxn":
                    wage = float(pdf.monetary(worker_wage)) * MXN
                    wage = int(pdf.monetary(wage, dot=False))
                    security = (wage + worker_desk) * 2
                if worker_onboard is not None:
                    security = security - worker_onboard
                if security == 0:
                    print(f"no security deposity for {worker_name}")
                elif security < 0:
                    print(f"security is negative for {worker_name}: {security}")
                elif security > 0:
                    if self.customer_source_type == "card":
                        security = float(pdf.monetary(security)) * 1.04
                        security = int(pdf.monetary(security, dot=False))
                    total_charge += int(security)
                    charges.update({f"{worker_name} security": f"{pdf.monetary(security)}"})
                    # security_charge = payment.create_charge(self.customer_stripe_id, security, self.customer_currency, f"{worker_name}'s security deposit")
                    # print(f"security charge id for {worker_name}: {security_charge.id}")

                
                ## conferir o currency
                ## conferir se ele ja nao trabalhava ano passado
                # christmas bonus
                if self.customer_christmas == "1" and worker_christmas_id is None:
                # confere se o worker trabalha ate 4 meses antes do natal
                    today = datetime.now()
                    december = datetime(today.year, 12, 3, 0, 0)
                    if today.month > 12:
                        december = datetime(today.year + 1, 12, 3, 0, 0)
                    now = datetime.now()
                    months_until_december = (december - now).days / 30
                    months_until_december = int(months_until_december)
                    if months_until_december >= 4:
                        christmas_amount = worker_wage + int(worker_wage / 14)
                        if worker_currency_wage == "usd":        
                            christmas_amount = float(pdf.monetary(christmas_amount)) * MXN
                        if self.customer_source_type == "card":
                            christmas_amount = float(pdf.monetary(christmas_amount)) * 1.04
                        christmas_amount = int(pdf.monetary(christmas_amount, dot=False))
                        christmas_sub = payment.create_christmas_subscription(self.customer_stripe_id, worker_name, christmas_amount, self.customer_currency)
                        dbutil.update_item("christmas_id", christmas_sub.id, worker[0], table="workers")
                        
                    else:
                        print("christmas bonus not necessary")
                        ## create a confirmation for christmas bonus
                    ## add to database

                # create a desk price
                if worker_desk_id is None:

                    ### conferir o uso disso
                    if self.customer_currency == "mxn":
                        worker_desk = float(pdf.monetary(worker_desk)) * MXN
                    if self.customer_source_type == "card":
                        worker_desk = float(pdf.monetary(worker_desk)) * 1.04
                    worker_desk = int(pdf.monetary(worker_desk, dot=False))
                    desk = payment.create_desk_price(worker_name, worker_desk, self.customer_currency)
                    
                    desk_sub = payment.create_subscription(self.customer_stripe_id, desk.id, cancel=44, currency=self.customer_currency, description=f"{worker_name}'s desk subscription")
                    dbutil.update_item("desk_id", desk_sub.id, worker[0], table="workers")
                    print(f"desk subscription id: {desk_sub.id}")


                # create a wage price
                if worker_wage_id is None:
                    # confere o currency do wage
                    if self.customer_currency == worker_currency_wage:
                        wage_amount = worker_wage
                    elif self.customer_currency == "usd" and worker_currency_wage == "mxn":
                        wage_amount = float(pdf.monetary(worker_wage)) * MXN
                    elif self.customer_currency == "mxn" and worker_currency_wage == "usd":
                        rate = pdf.get_rate('USD-MXN')
                        wage_amount = float(pdf.monetary(worker_wage)) * rate
       
                    if self.customer_source_type == "card":
                        wage_amount = float(wage_amount) * 1.04
                    wage_amount = int(pdf.monetary(wage_amount, dot=False))
                    wage = payment.create_worker_price(worker_name, wage_amount, self.customer_currency)   
                    print(f"wage subscription id:{wage.id}")

                        # 48 weeks - 4 weeks for security
                    wage_sub = payment.create_subscription(self.customer_stripe_id, wage.id, cancel=44, currency=self.customer_currency, description=f"{worker_name}'s wage")
                    dbutil.update_item("wage_id", wage_sub.id, worker[0], table="workers")
                    print(f"wage subscription id: {wage_sub.id}")

        charge = payment.create_charge(self.customer_stripe_id, total_charge, self.customer_currency, charges)
        print(charge.id)
        total_charge = 0
        charges = []
        print("payments submitted! \n")
        # if success:
        #     print("success!")
        # else:
        #     print("failed!")


                

        ## deve conferir os que ja existem e os que devem ser adicionados
            # isso facilitara para excluir um worker especifico no futuro
        
                # create a subscription


    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
