import json

# get key from keys.json
def get_api_key(currency="usd"):
    with open("components/keys.json") as f:
        keys = json.load(f)
    if currency == "usd":
        return keys["usd"]
    elif currency == "mxn":
        return keys["mxn"]

x = get_api_key()
print(x)

