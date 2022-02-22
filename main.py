from operator import itemgetter

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

# import components.to_pdf_class as pdf
import components.DButilC as dbutil


class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("components/ui.kv")

        # to avoid bugs
        self.currency_check = False

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
                "text": dbutil.get_item("name", i, "id"),
                "height": dp(56),
                "on_release": lambda x=dbutil.get_item(
                    "name", i, "id"
                ): self.set_customer(x),
            }
            for i in range(0, dbutil.get_qtd())
        ]
        # sort list alphabetically, the last customer create a bug, so the dropdown dont show it

        menu_items_customer_sorted = sorted(menu_items_customer, key=itemgetter("text"))

        self.customer_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_customer,
            items=menu_items_customer_sorted,
            position="center",
            width_mult=4,
        )

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

    def set_customer(self, text_item):
        self.kv.ids.drop_customer.set_item(text_item)
        self.customer_menu.dismiss()
        print(text_item)
        self.customer = text_item
        self.root.ids.licensee.text = text_item
        self.customer_id = dbutil.get_item("id", text_item, "name")
        self.customer_row = dbutil.get_row(self.customer_id)
        print(self.customer_row)
        if self.customer_row[2] is not None:
            self.root.ids.company.text = self.customer_row[2]
        else:
            self.root.ids.company.text = ""

        if self.customer_row[4] is not None:
            self.root.ids.phone.text = self.customer_row[4]
        else:
            self.root.ids.phone.text = ""
        if self.customer_row[5] is not None:
            self.root.ids.email.text = self.customer_row[5]
        else:
            self.root.ids.email.text = ""

    def check_currency(self, checkbox, active):
        if active:
            self.currency_check = True
            self.root.ids.onboard.hint_text = "Onboard (MXN)"
            self.root.ids.security.hint_text = "Security deposit (MXN)"
            self.root.ids.apartment.hint_text = "Apartment (MXN)"
        if not active:
            self.currency_check = False
            self.root.ids.onboard.hint_text = "Onboard (USD)"
            self.root.ids.security.hint_text = "Security deposit (USD)"
            self.root.ids.apartment.hint_text = "Apartment (USD)"

    def submit(self):
        if self.currency_check:
            self.currency = "MXN"
        else:
            self.currency = "USD"

        # add to database
        item_dict = {
            "name": self.customer,
            "currency": self.currency,
            "company": self.root.ids.company.text,
            "phone": self.root.ids.phone.text,
            "email": self.root.ids.email.text,
            "licensor": self.root.ids.licensor.text,
            "local": self.specific_location,
            "onboard": self.root.ids.onboard.text,
            "security": self.root.ids.security.text,
            "apartment": self.root.ids.apartment.text,
        }
        try:
            dbutil.insert_data_customer(item_dict)
        except:
            print("customer already exists, try update!")
        # add to dropdowns

    def submit_payment_method(self):
        pass

    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
