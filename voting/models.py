from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from stellar_sdk import Keypair, TransactionBuilder, Asset
from .stellar_utils import create_stellar_account, fund_account
from voting_project.settings import STELLAR_SERVER, STELLAR_NETWORK  # Use proper settings for server and network


# User Model
class User(AbstractUser):
    government_id = models.CharField(max_length=255, unique=True)
    stellar_wallet_address = models.CharField(max_length=56, blank=True, null=True)  # Stellar public key
    stellar_secret_key = models.CharField(max_length=56, blank=True, null=True)  # Stellar secret key
    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Custom related name to avoid conflicts
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Custom related name to avoid conflicts
        blank=True,
    )


@receiver(post_save, sender=User)
def generate_stellar_account(sender, instance, created, **kwargs):
    if created and not instance.stellar_wallet_address:
        stellar_account = create_stellar_account()
        instance.stellar_wallet_address = stellar_account["public_key"]
        instance.stellar_secret_key = stellar_account["secret_key"]
        instance.save()

        # Fund account on Stellar testnet
        fund_account(instance.stellar_wallet_address)


# Election Model
class Election(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    stellar_account = models.CharField(max_length=56, blank=True, null=True)  # Election Stellar account public key
    stellar_secret_key = models.CharField(max_length=56, blank=True, null=True)  # Election Stellar account secret key
    token_name = models.CharField(max_length=255)
    token_issuer = models.CharField(max_length=56, blank=True, null=True)  # Token issuer public key

    def issue_tokens(self):
        # Create Stellar account for the election if not already created
        if not self.stellar_account:
            stellar_account = create_stellar_account()
            self.stellar_account = stellar_account["public_key"]
            self.stellar_secret_key = stellar_account["secret_key"]
            self.save()

        # Fund the election's Stellar account
        fund_account(self.stellar_account)

        # Issue token
        asset = Asset(self.token_name, self.stellar_account)
        return asset

    def __str__(self):
        return self.name


# Candidate Model
class Candidate(models.Model):
    election = models.ForeignKey(Election, related_name="candidates", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stellar_address = models.CharField(max_length=56)  # Candidate's Stellar public key

    def __str__(self):
        return self.name


# Vote Model
class Vote(models.Model):
    election = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name="votes", on_delete=models.CASCADE)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)  # Stellar transaction hash

    def cast_vote(self):
        # Ensure the election's tokens are issued
        token_asset = self.election.issue_tokens()

        # Load Stellar account for the voter
        user_keypair = Keypair.from_secret(self.user.stellar_secret_key)

        # Build and submit the transaction
        transaction = (
            TransactionBuilder(
                source_account=STELLAR_SERVER.load_account(user_keypair.public_key),
                network_passphrase=STELLAR_NETWORK.passphrase,
                base_fee=100
            )
            .add_text_memo(f"Vote for {self.candidate.name}")
            .append_payment_op(
                destination=self.candidate.stellar_address,
                asset=token_asset,
                amount="1"
            )
            .build()
        )

        transaction.sign(user_keypair)
        try:
            response = STELLAR_SERVER.submit_transaction(transaction)
            self.transaction_hash = response["hash"]
            self.save()
        except Exception as e:
            raise Exception(f"Transaction failed: {str(e)}")

    def __str__(self):
        return f"Vote by {self.user.username} for {self.candidate.name}"
