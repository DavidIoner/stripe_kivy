from kivy.lang import Builder
from kivymd.app import MDApp
# import components.to_pdf_class as pdf
import components.DButil as dbutil

from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu


class App(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.kv = Builder.load_file('components/ui.kv')
		menu_items = [
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 1",
                "height": dp(56),
                "on_release": lambda x=f"#1 2DA CERRADA LAGO BOLSENA": self.set_item(x),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 2 (not available)",
                "height": dp(56),
                "on_release": lambda x=f"#2": self.set_item(x),
            }, 
            {
                "viewclass": "OneLineIconListItem",
                "text": f"local 3 (not available)",
                "height": dp(56),
                "on_release": lambda x=f"#3": self.set_item(x),
            } 
        ]
		self.menu = MDDropdownMenu(
            caller=self.kv.ids.drop_local,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        
	def set_item(self, text_item):
		self.kv.ids.drop_local.set_item(text_item)
		self.menu.dismiss()
		print(text_item)
		if "#1" in text_item:
			self.specific_location = "2DA CERRADA LAGO BOLSENA #54, LAGO NORTE DF, MIGUEL HIDALGO, DF. MX"
			self.location = "Mexico City, Mexico"
			self.city = "Mexico City"
		else:
			self.specific_location = text_item
	
	def submit(self):
		# dbutil.insert_data(
		pass
        
	def handle_key(self):
		pass

	def build(self):
		return self.kv
		

App().run()