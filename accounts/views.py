from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("skills:dashboard")

    def form_valid(self, form):
        user = form.save()
        # Auto-login the freshly created user so registration → dashboard is one step.
        login(self.request, user)
        messages.success(self.request, "Welcome aboard! Your account is ready.")
        return redirect(self.success_url)
