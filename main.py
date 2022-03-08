from operator import itemgetter

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

# import components.to_pdf_class as pdf
import components.DButilC as dbutil
import components.payment as payment

class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("components/ui.kv")

        # to avoid bugs
        self.currency_check = False
        self.customer_id = None
        
        menu_items_local = [
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 1",
                "height": dp(56),
                "on_release": lambda x=f"#1 2DA CERRADA LAGO BOLSENA": self.set_local(
                    x
                ),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 2 (not available)",
                "height": dp(56),
                "on_release": lambda x=f"#2": self.set_local(x),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 3 (not available)",
                "height": dp(56),
                "on_release": lambda x=f"#3": self.set_local(x),
            },
        ]

        self.local_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_local,
            items=menu_items_local,
            position="center",
            width_mult=4,
        )
        
        menu_items_customer = [
            {
                "viewclass": "OneLineIconListItem",
                "text": customer[1],
                "height": dp(56),
                "on_release": lambda x=f'{customer[1]}': self.set_customer(customer[0])}
            
            for customer in dbutil.get_all()
        ]


        self.customer_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_customer,
            items=menu_items_customer,
            position="bottom",
            width_mult=4,
        )


    ## usar somente o numero e pegar no banco pelo id
    def set_local(self, text_item):
        self.kv.ids.drop_local.set_item(text_item)
        self.local_menu.dismiss()
        print(text_item)
        if "#1" in text_item:
            self.specific_location = (
                "2DA CERRADA LAGO BOLSENA #54, LAGO NORTE DF, MIGUEL HIDALGO, DF. MX"
            )
            self.location = "Mexico City, Mexico"
            self.city = "Mexico City"
        else:
            self.specific_location = text_item

    #### Terminar o codigo abaixo ####
    def set_customer(self, customer_id):
        self.customer_row = dbutil.get_row(customer_id)
        self.kv.ids.drop_customer.set_item(self.customer_row[1])
        self.customer_menu.dismiss()
        print(self.customer_row)
        
        # set fields
        self.root.ids.customer.text = self.customer_row[1]
        if self.customer_row[2] is not None:
            self.root.ids.company.text = self.customer_row[2]
        else:
            self.root.ids.company.text = ""
        if self.customer_row[3] is not None:
            self.root.ids.located_at.text = self.customer_row[3]
        else:
            self.root.ids.located_at.text = ""
        if self.customer_row[4] is not None:
            self.root.ids.phone.text = self.customer_row[4]
        else:
            self.root.ids.phone.text = ""
        if self.customer_row[5] is not None:
            self.root.ids.email.text = self.customer_row[5]
        else:
            self.root.ids.email.text = ""
        if self.customer_row[6] is not None:
            self.root.ids.licensor.text = self.customer_row[6]
        else:
            self.root.ids.licensor.text = ""
        if self.customer_row[8] is not None:
            self.root.ids.onboard.text = str(self.customer_row[8])
        else:
            self.root.ids.onboard.text = ""
        if self.customer_row[9] is not None:
            self.root.ids.apartment.text = str(self.customer_row[9])
        else:
            self.root.ids.apartment.text = ""
        # if self.customer_row[7] is not None:
        #     self.set_local(self.customer_row[7])
        # else:
        #     self.set_local(0)
        if self.customer_row[10] is not None:
            pass
        

    def check_currency(self, checkbox, active):
        if active:
            self.currency_check = True
            self.root.ids.onboard.hint_text = "Onboard (MXN)"
            self.root.ids.apartment.hint_text = "Apartment (MXN)"
        if not active:
            self.currency_check = False
            self.root.ids.onboard.hint_text = "Onboard (USD)"
            self.root.ids.apartment.hint_text = "Apartment (USD)"

    def submit(self):
        if self.currency_check:
            self.currency = "mxn"
        else:
            self.currency = "usd"

        if self.root.ids.onboard.text == "":
            self.root.ids.onboard.text = "0"
        if self.root.ids.apartment.text == "":
            self.root.ids.apartment.text = "0"

        # add to database
        item_dict = {
            "name": self.root.ids.customer.text,
            "currency": self.currency,
            ## ajustar local!
            "located_at": "localidade",
            "company": self.root.ids.company.text,
            "phone": self.root.ids.phone.text,
            "email": self.root.ids.email.text,
            "licensor": self.root.ids.licensor.text,
            "local": self.specific_location,
            "onboard": self.root.ids.onboard.text,
            "apartment": self.root.ids.apartment.text,
        }
        try:
            # print(item_dict)
            dbutil.insert_data_customer(item_dict)
            # customer_id = dbutil.get_last_id()
            # print(f'customer id: {customer_id}')
            # self.customer_row = dbutil.get_row(customer_id)
        except:
            print("customer already exists, try update!")
        # add to dropdowns
        # try:
        #     if dbutil.verify_row(self.root.ids.customer.text):
        #         self.customer_row = dbutil.get_row(self.customer_id)

        #     ### MAKE TESTS ###
        #     if self.customer_row[12] is None:
        #         customer = payment.create_customer(self.customer_row[1], self.customer_row[5])
        #         dbutil.update_item("customer_id", customer.id, self.customer_id)
        # except:
        #     print("error!")

    def submit_payment_method(self):       
        card = self.root.ids.card_number.text
        cvc = self.root.ids.cvv.text
        exp_month = self.root.ids.exp_month.text
        exp_year = self.root.ids.exp_year.text
        ### MAKE TESTS ###
        if self.customer_row[11] is None:
            try:
                source = payment.create_source(self.customer_row[5], card, exp_month, exp_year, cvc)
                customer = payment.create_customer(self.customer_row[1], self.customer_row[5], source.id)
                dbutil.update_item("customer_id", customer.id, self.customer_id)
            except:
                print("error! (create customer payment)")


    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
