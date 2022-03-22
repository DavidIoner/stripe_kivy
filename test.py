import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf
import stripe

MXN = pdf.get_rate('MXN-USD')
p = int(pdf.monetary(MXN, dot=False))
print(MXN)
print(p)
