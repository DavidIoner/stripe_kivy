from operator import itemgetter

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

        menu_items_customer = [
            {
                "viewclass": "OneLineIconListItem",
                "text": dbutil.get_item("name", i, "id"),
                "height": dp(56),
                "on_release": lambda x=f'{i} {dbutil.get_item("name", i, "id")}': self.set_customer(x)}
            
            for i in range(0, dbutil.get_qtd())
        ]


        self.customer_menu = MDDropdownMenu(
            caller=self.kv.ids.drop_customer,
            items=menu_items_customer,
            position="bottom",
            width_mult=4,
        )

    def set_customer(self, text_item):
        self.customer_id = int(text_item[0])
        self.kv.ids.drop_customer.set_item(text_item)
        self.customer_menu.dismiss()
        self.customer_row = dbutil.get_row(self.customer_id)


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
        if self.root.ids.christmas.text == 0:
            christmas = None

        item_dict = {
            "customer": self.customer_row[1],
            "holiday": self.holiday,
            "name": self.root.ids.worker.text,
            "wage": self.root.ids.wage.text,
            "christmas": christmas,
            "desk": self.root.ids.desk.text,
        }
        print(item_dict)
        try:
            dbutil.insert_data_worker(item_dict)
        except:
            print("worker already exists or the data is invalid")
        # add to dropdowns

    def generate_pdf(self):
        ## GENERATE CUSTOMER PART ##
        customer_pdf = pdf.Report(self.customer_id)
        customer_pdf.create_customer()
        ## GENERATE WORKER PART ##
        exibith = 0
        for i in range(1, dbutil.get_qtd(table="workers")+1):
            row = dbutil.get_row(i, table="workers")
            if row[1] == self.customer_row[1]:
                exibith += 1
                worker_pdf = pdf.Report(row[0])
                worker_pdf.create_worker()


        ## MERGE THE CONTRACTS ##

        # DELETE THE TEMP PDFS #


    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
