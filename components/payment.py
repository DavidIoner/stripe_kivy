import stripe
import datetime
from datetime import timedelta


# create a customer
def create_customer(name, email, source=None, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    if source is None:
        customer = stripe.Customer.create(
            name=name,
            email=email,
        )
        return customer
    else:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            source=source,
        )
        return customer


def create_source(email, card_number, exp_month, exp_year, cvc, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Source.create(
        type='card',
        currency='usd',
        card={
            "number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
        },
        owner={
            "email": email,}
    )


# create a price with the worker id
def create_desk_price(worker_name, amount, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Price.create(
        currency=currency,
        unit_amount=amount,
        nickname=f"{worker_name}_desk_price",
        recurring={
            "interval": "week",
            "interval_count": 2,
        },
        product_data={
            "name": f"{worker_name}_desk",
            "type": "service",
        },
    )


def create_worker_price(worker_name, amount, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"

    # get the date after 12 months
    return stripe.Price.create(
        currency=currency,
        unit_amount=amount,
        nickname=f"{worker_name}_service_price",
        recurring={
            "interval": "week",
            "interval_count": 2,
        },
        product_data={
            "name": f"{worker_name}_service",
            "type": "service",
        },
    )


# create a subscription with the worker id
def create_subscription(customer_id, price, cancel=12, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
        
    cancel_at = datetime.datetime.now() + timedelta(months=cancel)
    return stripe.Subscription.create(
        customer=customer_id,
        cancel_at=cancel_at,
        items=[
            {
                "price": price,
                "quantity": 1,
            }
        ],
    )


# create a charge for a customer
def create_charge(customer_id, amount, source, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Charge.create(
        customer=customer_id,
        amount=amount,
        source=source,
        currency=currency,
        description="Charge for" + customer_id,
    )


# create an invoice for a customer
def create_invoice(
    customer_id, subscription_id, collection_method="send_invoice", currency="usd"
):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Invoice.create(
        customer=customer_id,
        subscription=subscription_id,
        collection_method=collection_method,
        currency=currency,
    )


# retrieve a customer
def retrieve_customer(customer_id, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Customer.retrieve(customer_id)

