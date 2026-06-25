import requests
import os

SECRET = os.getenv("PAYSTACK_SECRET")

def init_payment(email, amount):
    return requests.post(
        "https://api.paystack.co/transaction/initialize",
        headers={"Authorization": f"Bearer {SECRET}"},
        json={
            "email": email,
            "amount": amount * 100
        }
    ).json()