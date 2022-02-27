import components.to_pdf as pdf
import components.DButilC as dbutil

def generate_pdf():
    customer = pdf.Report(1)
    exibith = 0
    customer_row = dbutil.get_row(1)
    for i in range(1, dbutil.get_qtd(table="workers")+1):
        row = dbutil.get_row(i, table="workers")
        if row[1] == customer_row[1]:
            exibith += 1
            worker_pdf = pdf.Report(row[0])
            worker_pdf.create_worker()

report = pdf.Report(4)
report.create_worker(3, 1)
