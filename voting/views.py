from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Candidate, Election, Vote
from django.contrib import messages
from collections import Counter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Candidate, Election, Vote
from stellar_sdk.exceptions import BadRequestError  # Import the Stellar error


def register(request):
    if request.user.is_authenticated:
        return redirect("election_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect("login")
        else:
            messages.error(request, "Error in registration. Please check the details.")
    else:
        form = UserCreationForm()
    return render(request, "voting/register.html", {"form": form})


def election_list(request):
    elections = Election.objects.all()
    return render(request, "voting/elections.html", {"elections": elections})





def vote(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    if request.method == "POST":
        candidate_id = request.POST.get("candidate")
        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Prevent duplicate votes
        if Vote.objects.filter(user=request.user, election=election).exists():
            messages.error(request, "You have already voted in this election.")
            return redirect("election_list")

        try:
            # Try funding the account (if required) before casting the vote
            fund_account(request.user.username)  # Adjust this function to your funding logic
        except BadRequestError as e:
            # Handle "account already funded" gracefully
            if "account already funded to starting balance" in str(e):
                messages.info(request, "Account already funded. Proceeding with vote.")
            else:
                messages.error(request, "Failed to fund account. Please try again.")
                return redirect("election_list")

        # Cast the vote after ensuring the account is funded
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        messages.success(request, "Your vote has been cast!")
        return redirect("election_list")

    return render(request, "voting/vote.html", {"election": election, "candidates": candidates})



def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    votes = election.votes.all()

    # Count votes and sort by the number of votes
    results = Counter(vote.candidate for vote in votes)
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

    return render(request, "voting/results
