from stellar_sdk import Keypair
import requests


def create_stellar_account():
    """Creates a new Stellar account keypair."""
    keypair = Keypair.random()
    return {"public_key": keypair.public_key, "secret_key": keypair.secret}


def fund_account(public_key):
    """Funds a Stellar account on the testnet using Friendbot."""
    url = f"https://friendbot.stellar.org/?addr={public_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fund account: {response.content}")
    return response.json()
