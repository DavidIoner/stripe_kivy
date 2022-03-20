from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
import components.to_pdf as pdf
import components.DButilC as dbutil
import components.payment as payment



class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("components/worker_ui.kv")

        # to avoid bugs
        self.holiday_check = False
        self.customer_row = None
        self.currency_wage = False

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
        #### AJEITAR ISSO AQUI ####
        self.customer_id = self.customer_row[0]
        self.customer_name = self.customer_row[1]
        self.customer_email = self.customer_row[5]
        self.customer_currency = self.customer_row[8]
        self.customer_christmas = self.customer_row[9]
        self.customer_stripe_id = self.customer_row[10]
       
        self.kv.ids.drop_customer.set_item(self.customer_name)
        self.customer_menu.dismiss()

        if self.customer_currency == "usd":
            self.root.ids.onboard.hint_text = "Onboard (USD)"
        elif self.customer_currency == "mxn":
            self.root.ids.onboard.hint_text = "Onboard (MXN)"

        ## mostrar a lista dos workers desse customer (pelo menos o nome e a qtd em um menu)

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
                "holiday": self.holiday,
                "name": self.root.ids.worker.text,
                "wage": self.root.ids.wage.text,
                "desk": self.root.ids.desk.text,
                "onboard": self.root.ids.onboard.text,
            })

            # add to database
            try:
                dbutil.insert_data_worker(item_dict)
            except:
                print("worker already exists or the data is invalid")
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


        pdf.merge_pdf(pdf_list, self.customer_name)
        pdf.delete_temp_files()
        ## send email


    ## criar as subscriptions e charges correspondentes
    def submit_payments(self):
        # confere se o customer tem um stripe_id
        if self.customer_stripe_id is None:
            # create a customer
            customer = payment.create_customer(self.customer_name, self.customer_email, currency=self.customer_currency)
            dbutil.update_item("customer_id", customer.id, self.customer_id, table="customers")
         


        # subscriptions and worker prices
        for worker in dbutil.get_all("workers"):
            worker_customer = worker[1]
            # confere a relacao do worker com o customer
            if worker_customer== self.customer_name:
                #### AJEITAR ISSO AQUI ####
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
                    apartment = payment.create_charge(self.customer_stripe_id, worker_apartment, self.customer_currency, f"{worker_name}'s apartment")
                    print(f"apartment charge id: {apartment.id}")

                # create security charge
                if worker_currency_wage == "usd":
                    security = (worker_wage + worker_desk) * 2
                    security = security - worker_onboard
                else:
                    wage = worker_wage * pdf.get_rate('MXN-USD')
                    security = (wage + worker_desk) * 2
                    security = security - worker_onboard
                if security == 0:
                    print(f"no security deposity for {worker_name}")
                elif security < 0:
                    print(f"security is negative for {worker_name}: {security}")
                elif security > 0:
                    security_charge = payment.create_charge(self.customer_stripe_id, security, self.customer_currency, f"{worker_name}'s security deposit")
                    print(f"security charge id for {worker_name}: {security_charge.id}")

                
                
                
                
                ## conferir o currency
                # christmas bonus
                if self.customer_christmas == "1":
                # confere se o worker trabalha ate 4 meses antes do natal
                    today = datetime.now()
                    december = datetime(today.year, 12, 3, 0, 0)
                    if today.month > 12:
                        december = datetime(today.year + 1, 12, 3, 0, 0)
                    now = datetime.now()
                    months_until_december = (december - now).days / 30
                    months_until_december = int(months_until_december)
                    if months_until_december >= 4:
                        amount = worker_wage + int(worker_wage / 14)
                        if worker_currency_wage == "usd":
                            rate = pdf.get_rate('MXN-USD')
                            amount *= int(pdf.monetary(rate, dot=False))
                        christmas_sub = payment.create_christmas_subscription(self.customer_stripe_id, worker_name, amount, self.customer_currency)
                        dbutil.update_item("christmas_id", christmas_sub.id, worker[0], table="workers")
                        
                    else:
                        print("christmas bonus not necessary")
                        ## create a confirmation for christmas bonus
                    ## add to database

                # create a desk price
                if worker_desk_id is None:
                    if self.customer_currency == "usd":
                        desk = payment.create_desk_price(worker_name, worker_desk, self.customer_currency)

                    ### conferir o uso disso
                    if self.customer_currency == "mxn":
                        rate = pdf.get_rate('MXN-USD')
                        worker_desk *= int(pdf.monetary(rate, dot=False))
                        desk = payment.create_desk_price(worker_name, worker_desk, self.customer_currency)
                    print(f"desk: {desk.id}")
                    try:
                        ## save the subscription not the price
                        desk_sub = payment.create_subscription(self.customer_stripe_id, desk.id, currency=self.customer_currency)
                        dbutil.update_item("desk_id", desk_sub.id, worker[0], table="workers")
                        print(f"desk subscription id: {desk_sub.id}")
                    except:
                        print("error updating wage_id or creating subscription for desk")

                # create a wage price
                if worker_wage_id is None:
                    # confere o currency do wage
                    if self.customer_currency == worker_currency_wage:
                        amount = worker_wage
                    elif self.customer_currency == "usd" and worker_currency_wage == "mxn":
                        rate = pdf.get_rate('MXN-USD')
                        amount = worker_wage * int(pdf.monetary(rate, dot=False))
                    elif self.customer_currency == "mxn" and worker_currency_wage == "usd":
                        rate = pdf.get_rate('USD-MXN')
                        amount = worker_wage * int(pdf.monetary(rate, dot=False))
                    
                    wage = payment.create_worker_price(worker_name, amount, self.customer_currency)   
                    print(f"wage:{wage.id}")
                    try:
                        # 48 weeks - 4 weeks for security
                        wage_sub = payment.create_subscription(self.customer_stripe_id, wage.id, cancel=44, currency=self.customer_currency)
                        dbutil.update_item("wage_id", wage_sub.id, worker[0], table="workers")
                        print(f"wage subscription id: {wage_sub.id}")
                    except:
                        print("error updating wage_id or creating subscription")

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
