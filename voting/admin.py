from django.contrib import admin
from .models import User, Election, Candidate, Vote

admin.site.register(User)
admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Vote)
