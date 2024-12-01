from stellar_sdk import Keypair
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, Network
from stellar_sdk.exceptions import BadRequestError


def create_stellar_account():
    """Creates a new Stellar account keypair."""
    keypair = Keypair.random()
    return {"public_key": keypair.public_key, "secret_key": keypair.secret}




def fund_account(account_id):
    server = Server("https://horizon.stellar.org")
    source_keypair = Keypair.from_secret("YOUR_SECRET_KEY")  # Replace with your source account
    source_account = server.load_account(source_keypair.public_key)

    # Check if the account already exists
    try:
        server.accounts().account_id(account_id).call()
        raise BadRequestError("Account already funded to starting balance")
    except BadRequestError:
        # Proceed to fund if account does not exist
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_create_account_op(destination=account_id, starting_balance="2.0")
            .build()
        )
        transaction.sign(source_keypair)
        server.submit_transaction(transaction)
