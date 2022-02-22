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
        self.kv = Builder.load_file("components/worker_ui.kv")

        # to avoid bugs
        self.holiday_check = False
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

    def set_customer(self, text_item):
        self.kv.ids.drop_customer.set_item(text_item)
        self.customer_menu.dismiss()
        self.customer = text_item
        self.customer_id = dbutil.get_item("id", text_item, "name")
        self.customer_row = dbutil.get_row(self.customer_id)
        # get toker from row

    def check_holiday(self, checkbox, active):
        if active:
            self.holiday_check = True

        if not active:
            self.holiday_check = False

    def submit(self):
        if self.holiday_check:
            self.holiday = "1"
        else:
            self.holiday = "0"
        # add to database
        item_dict = {
            "customer": self.customer,
            "holiday": self.holiday,
            "name": self.root.ids.worker.text,
            "wage": self.root.ids.wage.text,
            "christmas": self.root.ids.christmas.text,
            "desk": self.root.ids.desk.text,
        }
        try:
            dbutil.insert_data(item_dict)
        except:
            print("worker already exists, try update!")
        # add to dropdowns

    def submit_desk(self):
        pass

    def submit_wage(self):
        pass

    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
