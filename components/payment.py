import stripe
import datetime
from datetime import timedelta
from datetime import datetime
import json

# get api key from keys.json
def get_api_key(currency="usd"):
    with open("components/keys.json") as f:
        keys = json.load(f)
    if currency == "usd":
        return keys["usd"]
    elif currency == "mxn":
        return keys["mxn"]



# create a customer
def create_customer(name, email, source=None, currency="usd"):
    stripe.api_key = get_api_key(currency)

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
    stripe.api_key = get_api_key(currency)
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

def attach_source(customer_id, source, currency="usd"):
    stripe.api_key = get_api_key(currency)
    
    return stripe.Customer.create_source(
        customer=customer_id,
        source=source,
    )


# create a price with the worker id
def create_desk_price(worker_name, amount, currency="usd"):
    stripe.api_key = get_api_key(currency)
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
    stripe.api_key = get_api_key(currency)

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


## fazer cobrar so em 1 de dezembro uma vez
def create_christmas_price(worker_name, amount, currency="usd"):
    stripe.api_key = get_api_key(currency)

    return stripe.Price.create(
        currency=currency,
        unit_amount=amount,
        nickname=f"{worker_name}_christmas_price",
        recurring={
            "interval": "year",
            "interval_count": 1,
        },
        product_data={
            "name": f"{worker_name}_christmas",
            "type": "service",
        },
    )


# create a subscription with the worker id
def create_subscription(customer_id, price, cancel=48, currency="usd"):
    stripe.api_key = get_api_key(currency)

    end_date = datetime.now() + timedelta(weeks=cancel)
    end_date = str(end_date)[:10]
    epoch = datetime(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]), 0, 0).timestamp()
    epoch = int(epoch)

    return stripe.Subscription.create(
        customer=customer_id,
        cancel_at=epoch,
        items=[
            {
                "price": price,
                "quantity": 1,
            }
        ],
    )


# create a charge for a customer
def create_charge(customer_id, amount, currency="usd", description="charge"):
    stripe.api_key = get_api_key(currency)

    return stripe.Charge.create(
        customer=customer_id,
        amount=amount,
        currency=currency,
        description=description,
    )


# create an invoice for a customer
def create_invoice(
    customer_id, subscription_id, collection_method="send_invoice", currency="usd"
):
    stripe.api_key = get_api_key(currency)

    return stripe.Invoice.create(
        customer=customer_id,
        subscription=subscription_id,
        collection_method=collection_method,
        currency=currency,
    )


# retrieve a customer
def retrieve_customer(customer_id, currency="usd"):
    stripe.api_key = get_api_key(currency)

    return stripe.Customer.retrieve(customer_id)

