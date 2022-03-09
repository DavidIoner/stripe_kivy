from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from PyPDF2 import PdfFileMerger
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

    def set_customer(self, customer_id):
        self.customer_row = dbutil.get_row(customer_id)
        self.customer_id = customer_id
        self.kv.ids.drop_customer.set_item(self.customer_row[1])
        self.customer_menu.dismiss()
        ## mostrar a lista dos workers desse customer (pelo menos o nome e a qtd em um menu)


    def check_holiday(self, checkbox, active):
        if active:
            self.holiday_check = True

        if not active:
            self.holiday_check = False

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

            item_dict.update({
                "customer": self.customer_row[1],
                "holiday": self.holiday,
                "name": self.root.ids.worker.text,
                "wage": self.root.ids.wage.text,
                "desk": self.root.ids.desk.text,
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
                # create a price for that worker
                try:

                    desk = payment.create_desk_price(worker_row[2], worker_row[5], self.customer_row[10])
                    print(desk)
                    dbutil.update_item("desk_id", desk.id, worker_row[0], "workers")
                    wage = payment.create_worker_price(worker_row[2], worker_row[3], self.customer_row[10])
                    print(wage)
                    dbutil.update_item("wage_id", wage.id, worker_row[0], "workers")
                    # merge the pdfs
                except:
                    print(f'error, could not create desk or wage price for {worker_row[2]}')

        pdf.merge_pdf(pdf_list, self.customer_row[1])

        # exluir os pdfs temporarios
        # send email


    ## criar as subscriptions e charges correspondentes
    def submit_payments(self):

        ## deve conferir os que ja existem e os que devem ser adicionados
            # isso facilitara para excluir um worker especifico no futuro
        pass

    def update(self):
        pass

    def handle_key(self):
        pass

    def build(self):
        return self.kv


if __name__ == "__main__":
    App().run()
