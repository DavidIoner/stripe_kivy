import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf

worker_wage = 20000



amount = float(pdf.monetary(worker_wage)) + float(pdf.monetary(worker_wage / 14, dot=False))
print(pdf.monetary(amount))