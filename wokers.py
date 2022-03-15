from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
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
        self.customer_id = self.customer_row[0]
        self.kv.ids.drop_customer.set_item(self.customer_row[1])
        self.customer_menu.dismiss()

        if self.customer_row[10] == "usd":
            self.root.ids.onboard.hint_text = "Onboard (USD)"
        elif self.customer_row[10] == "mxn":
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

            if self.root.ids.christmas.text == 0:
                christmas = None
                item_dict.update({"christmas": christmas})
            else:
                christmas = self.root.ids.christmas.text
                item_dict.update({"christmas": christmas})

            if self.currency_wage == True:
                currency_wage = "usd"
                item_dict.update({"currency_wage": currency_wage})
            else:
                currency_wage = "mxn"
                item_dict.update({"currency_wage": currency_wage})
            


            item_dict.update({
                "customer": self.customer_row[1],
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
            if worker_row[1] == self.customer_row[1]:
                exibith += 1
                worker = gen_pdf.create_worker(worker_row[0], exibith)
                pdf_list.append(worker)


        pdf.merge_pdf(pdf_list, self.customer_row[1])
        pdf.delete_temp_files()
        ## send email


    ## criar as subscriptions e charges correspondentes
    def submit_payments(self):
        if self.customer_row[12] is None:
            # create a customer
            customer = payment.create_customer(self.customer_row[1], self.customer_row[5], currency=self.customer_row[10])
            dbutil.update_item("customer_id", customer.id, self.customer_row[0], table="customers")
        



        ## charges
        # apartment charge
        print("creating onboard charge...")
        onboard = payment.create_charge(self.customer_row[1], self.customer_row[8], self.customer_row[10])
        print(f"onboard charge id: {onboard.id}")

        
        ## confere se o worker trabalha ate 4 meses antes do natal



        # subscriptions and worker prices
        for worker in dbutil.get_all("workers"):
            # confere a relacao do worker com o customer
            if worker[1] == self.customer_row[1]:

                ## mudar para cada worker (apartment)
                print("creating apartment charge...")
                apartment = payment.create_charge(self.customer_row[1], self.customer_row[9], self.customer_row[10])
                print(f"apartment charge id: {apartment.id}")

                print("creating onboard charge...")
                onboard = payment.create_charge(self.customer_row[1], self.customer_row[8], self.customer_row[10])
                print(f"onboard charge id: {onboard.id}")
                
                
                # christmas bonus
                if self.customer_row[11] == "1":
                    amount = worker_row[3]
                    christmas = payment.create_price

                # create a desk price
                if worker[8] is None:
                    if self.customer_row[10] == "usd":
                        desk = payment.create_desk_price(worker[2], worker[5], self.customer_row[10])

                    ## conferir o uso disso
                    elif self.customer_row[10] == "mxn":
                        rate = pdf.get_rate('MXN-USD')
                        amount = worker[5] * int(pdf.monetary(rate, dot=False))
                        desk = payment.create_desk_price(worker[2], amount, self.customer_row[10])
                    print(f"desk: {desk.id}")
                    try:
                        dbutil.update_item("desk_id", desk.id, worker[0], table="workers")
                        worker_row = dbutil.get_row(worker[0], table="workers")
                        payment.create_subscription(self.customer_row[12], worker_row[8], currency=self.customer_row[10])
                    except:
                        print("error updating wage_id or creating subscription for desk")

                # create a wage price
                if worker[9] is None:
                    ## fazer isso se tornar uma fiução e chamar ela aqui
                    # confere o currency do wage
                    if self.customer_row[10] == worker[7]:
                        wage = payment.create_worker_price(worker[2], worker[3], currency=self.customer_row[10])
                        onboard = payment.create_charge(self.customer_id, amount * 2, self.customer_row[10], description=f"onboard {worker[2]}")  
                    elif self.customer_row[10] == "usd" and worker[7] == "mxn":
                        rate = pdf.get_rate('MXN-USD')
                        amount = worker[3] * int(pdf.monetary(rate, dot=False))
                        wage = payment.create_worker_price(worker[2], amount, self.customer_row[10])
                        onboard = payment.create_charge(self.customer_id, amount * 2, self.customer_row[10], description=f"onboard {worker[2]}")   
                    elif self.customer_row[10] == "mxn" and worker[7] == "usd":
                        rate = pdf.get_rate('USD-MXN')
                        amount = worker[3] * int(pdf.monetary(rate, dot=False))
                        wage = payment.create_worker_price(worker[2], amount, self.customer_row[10])   
                        onboard = payment.create_charge(self.customer_id, amount * 2, self.customer_row[10], description=f"onboard {worker[2]}")      
                    print(f"wage:{wage.id}")
                    payment.create_subscription(self.customer_row[12], worker[9], currency=self.customer_row[10])
                   
                    try:
                        dbutil.update_item("wage_id", wage.id, worker[0], table="workers")
                        worker_row = dbutil.get_row(worker[0], table="workers")
                        payment.create_subscription(self.customer_row[12], worker_row[9], currency=self.customer_row[10])
                    except:
                        print("error updating wage_id or creating subscription")




                

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
