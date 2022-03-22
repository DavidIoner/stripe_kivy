import components.payment as payment
from datetime import datetime
import components.to_pdf as pdf
import stripe

# get the full path with os
import components.send_pdf as send_pdf

send_pdf.send_email('/home/joberscreisom/projects/stripe_kivy/components/output/namee.pdf', 'davidhioner@gmail.com')