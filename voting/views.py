from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Candidate, Election, Vote
from django.contrib import messages
from collections import Counter

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful!")
            return redirect("login")
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
        vote = Vote.objects.create(user=request.user, election=election, candidate=candidate)
        vote.cast_vote()
        messages.success(request, "Your vote has been cast!")
        return redirect("election_list")

    return render(request, "voting/vote.html", {"election": election, "candidates": candidates})



def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    votes = election.votes.all()
    results = Counter(vote.candidate for vote in votes)
    return render(request, "voting/results.html", {"election": election, "results": results})
