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
        self.christmas_check = False
        self.customer_id = None
        
        menu_items_local = [
            {
                "viewclass": "OneLineIconListItem",
                "text": f"{local[3][:25]}",
                "height": dp(56),
                "on_release": lambda x=local[0]: self.set_local(x)}

            for local in dbutil.get_all("locals")
        ]
        self.local_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_local,
            items=menu_items_local,
            position="bottom",
            width_mult=4,
        )

        
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


        

    def set_local(self, local_id):
        self.local_row = dbutil.get_row(local_id, table="locals")
        self.kv.ids.drop_local.set_item(self.local_row[3][:25])
        self.local_menu.dismiss()


    #### Terminar o codigo abaixo ####
    def set_customer(self, customer_id):
        print(f'customer id: {customer_id}')
        self.customer_row = dbutil.get_row(customer_id)
        self.kv.ids.drop_customer.set_item(self.customer_row[1])
        self.customer_menu.dismiss()
        self.customer_id = customer_id
        self.customer_name = self.customer_row[1]
        self.company = self.customer_row[2]
        self.located_at = self.customer_row[3]
        self.phone = self.customer_row[4]
        self.email = self.customer_row[5]
        self.licensor = self.customer_row[6]
        self.local = self.customer_row[7]
        self.currency = self.customer_row[8]
        self.christmas = self.customer_row[9]
        self.customer_stripe_id = self.customer_row[10]

        
        # set fields
        self.root.ids.customer.text = self.customer_name
        if self.company is not None:
            self.root.ids.company.text = self.company
        else:
            self.root.ids.company.text = ""
        if self.located_at is not None:
            self.root.ids.located_at.text = self.located_at
        else:
            self.root.ids.located_at.text = ""
        if self.phone is not None:
            self.root.ids.phone.text = self.phone
        else:
            self.root.ids.phone.text = ""
        if self.email is not None:
            self.root.ids.email.text = self.email
        else:
            self.root.ids.email.text = ""
        if self.licensor is not None:
            self.root.ids.licensor.text = self.licensor
        else:
            self.root.ids.licensor.text = "Nigel Shamash"
        # if self.customer_row[7] is not None:
        #     self.set_local(self.customer_row[7])
        # else:
        #     self.set_local(0)
        # set checkboxes
        if self.currency == "mxn":
            self.root.ids.currency.active = True
        else:
            self.root.ids.currency.active = False
        if self.christmas == "1":
            self.root.ids.christmas.active = True
        else:
            self.root.ids.christmas.active = False
        

        

    def check_currency(self, checkbox, active):
        if active:
            self.currency_check = True
            self.root.ids.currency_label.text = "Currency is MXN!"
        if not active:
            self.currency_check = False
            self.root.ids.currency_label.text = "Currency is USD!"

    def check_christmas(self, checkbox, active):
        if active:
            self.christmas_check = True
            self.root.ids.christmas_label.text = "Christmas bonus active!"
        if not active:
            self.christmas_check = False
            self.root.ids.christmas_label.text = "Christmas bonus deactive!"

    def submit(self):
        if self.currency_check:
            self.currency = "mxn"
        else:
            self.currency = "usd"
        
        if self.christmas_check:
            christmas = "1"
        else:
            christmas = "0"
        

        # add to database
        item_dict = {
            "name": self.root.ids.customer.text,
            "currency": self.currency,
            "located_at": self.root.ids.located_at.text,
            "company": self.root.ids.company.text,
            "phone": self.root.ids.phone.text,
            "email": self.root.ids.email.text,
            "licensor": self.root.ids.licensor.text,
            "christmas": christmas,
            "local": self.local_row[0],
        }

        dbutil.insert_data_customer(item_dict)
        # set customer variables
        self.customer_id = dbutil.get_customer_id(self.root.ids.customer.text)
        self.set_customer(self.customer_id)

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


    def submit_payment_method(self):       
        card = self.root.ids.card_number.text
        cvc = self.root.ids.cvv.text
        exp_month = self.root.ids.exp_month.text
        exp_year = self.root.ids.exp_year.text
        ### MAKE TESTS ###

        try:
            # card payment method
            if card != "":
            ## if card is valid          
                source = payment.create_source(self.email, card, exp_month, exp_year, cvc, currency=self.currency)
                # confere se o customer existe e adiciona o source
                ## testar
                if self.customer_stripe_id is None:
                    customer = payment.create_customer(self.name, self.email, source.id, currency=self.currency)
                else:
                    payment.attach_source(self.customer_stripe_id, source.id)
            else:
                # invoice payment method
                print("invoice method is not inplemented yet! insert card data!")
            dbutil.update_item("customer_id", customer.id, self.customer_id, table="customers")
        except:
            print("error! (create customer payment)")


    def update_customer(self):
        print("this button is not implemented yet")
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
