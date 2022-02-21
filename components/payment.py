import stripe


# create a customer
def create_customer(name, email, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Customer.create(
        email=email,
        name=name,
        invoice_settings={
            "default_payment_method": None,
            "default_payment_due_days": 0,
        },
    )


# create a card payment method
def create_card_payment_method(
    customer_id, card_number, exp_month, exp_year, cvc, currency="usd"
):
    customer = retrieve_customer(customer_id)
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.PaymentMethod.create(
        type="card",
        card={
            "number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
        },
        billing_details={
            "name": customer.name,
        },
        metadata={
            "customer_id": customer_id,
        },
    )


# create a product with the worker id
def create_product(worker_name, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Product.create(
        name=worker_name,
        type="service",
    )


def create_desk_product(worker_name, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Product.create(
        name=f"{worker_name}_desk",
        type="service",
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
        # product=product_id,
        recurring={
            "interval": "day",
            "interval_count": 15,
        },
        product_data={
            "name": f"{worker_name}_desk",
            "type": "service",
        },
    )


def create_price(worker_name, amount, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Price.create(
        currency=currency,
        unit_amount=amount,
        nickname=f"{worker_name}_price",
        recurring={
            "interval": "day",
            "interval_count": 1,
        },
    )


# create a plan with the worker id
def create_plan(worker_name, amount, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Plan.create(
        nickname=worker_name,
        product=worker_name,
        amount=amount,
        currency=currency,
        interval="month",
        interval_count=1,
    )


# create a subscription with the worker id
def create_subscription(customer_id, worker_price, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Subscription.create(
        customer=customer_id,
        items=[
            {
                "price": worker_price,
                "quantity": 1,
            }
        ],
    )


# create a charge for a customer
def create_charge(customer_id, amount, currency="usd"):
    if currency == "usd":
        stripe.api_key = "sk_test_51KRRmAHPXOp77GbzAcFiks47OxjCBvuWHj3DbA9sSb1Du9oYJ3P8cyRrfTz77rHY9UP5MsnpuxxSCMzYMSWpbt37006nouDHA2"
    elif currency == "mxn":
        stripe.api_key = "mxnkey"
    return stripe.Charge.create(
        customer=customer_id,
        amount=amount,
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


# create a token for a customer card
