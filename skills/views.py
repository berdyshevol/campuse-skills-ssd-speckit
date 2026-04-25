from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import BookingRequestForm, ReviewForm, SkillForm
from .models import BookingRequest, Category, Review, Skill
from .permissions import OwnerOnlyMixin


class SkillListView(ListView):
    model = Skill
    template_name = "skills/skill_list.html"
    context_object_name = "skills"
    paginate_by = 12

    def get_queryset(self):
        # select_related avoids N+1 queries when the card renders category + owner.
        qs = Skill.objects.select_related("category", "owner").order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category")
        if q:
            qs = qs.filter(title__icontains=q)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["categories"] = Category.objects.filter(is_active=True)
        ctx["filters_active"] = bool(ctx["q"] or ctx["selected_category"])
        return ctx


class SkillDetailView(DetailView):
    model = Skill
    template_name = "skills/skill_detail.html"
    context_object_name = "skill"

    def get_queryset(self):
        return Skill.objects.select_related("category", "owner")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        skill = ctx["skill"]
        ctx["booking_form"] = BookingRequestForm()
        ctx["reviews"] = (
            skill.reviews.select_related("author").order_by("-created_at")[:20]
        )
        ctx["review_aggregate"] = skill.reviews.aggregate(
            avg=Avg("rating"), count=Count("id"),
        )
        user = self.request.user
        ctx["can_review"] = (
            user.is_authenticated
            and user != skill.owner
            and BookingRequest.objects.filter(
                requester=user, skill=skill,
                status=BookingRequest.Status.ACCEPTED,
            ).exists()
        )
        ctx["review_form"] = ReviewForm()
        return ctx


class SkillCreateView(LoginRequiredMixin, CreateView):
    """Authenticated users post new skills (FR-005, US2)."""

    model = Skill
    form_class = SkillForm
    template_name = "skills/skill_form.html"

    def form_valid(self, form):
        # The form does not expose `owner`; the view stamps the logged-in user.
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Skill posted.")
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "skills/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["requests_sent"] = (
            BookingRequest.objects.filter(requester=user)
            .select_related("skill", "skill__owner")
            .order_by("-created_at")
        )
        ctx["requests_received"] = (
            BookingRequest.objects.filter(skill__owner=user)
            .select_related("skill", "requester")
            .order_by("-created_at")
        )
        ctx["my_skills"] = (
            Skill.objects.filter(owner=user)
            .select_related("category")
            .order_by("-created_at")
        )
        return ctx


class SkillUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = "skills/skill_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Skill updated.")
        return response


class SkillDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView):
    model = Skill
    template_name = "skills/skill_confirm_delete.html"
    success_url = reverse_lazy("skills:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Skill deleted.")
        return response


class RequestBookingView(LoginRequiredMixin, View):
    """POST /skills/<pk>/request/ — create a BookingRequest in PENDING."""

    def post(self, request, pk: int):
        skill = get_object_or_404(Skill, pk=pk)
        # Defense in depth: the template already hides the form for owners.
        if request.user == skill.owner:
            return HttpResponseForbidden("You cannot book your own skill.")

        form = BookingRequestForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please correct the errors in the booking form.")
            return redirect("skills:detail", pk=skill.pk)

        booking = form.save(commit=False)
        booking.requester = request.user
        booking.skill = skill
        booking.status = BookingRequest.Status.PENDING
        try:
            booking.full_clean()
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
            return redirect("skills:detail", pk=skill.pk)
        booking.save()
        messages.success(request, "Booking request sent.")
        return redirect("skills:detail", pk=skill.pk)


class RespondRequestView(LoginRequiredMixin, View):
    """POST /requests/<pk>/respond/ — owner accepts or declines."""

    def post(self, request, pk: int):
        booking = get_object_or_404(
            BookingRequest.objects.select_related("skill"),
            pk=pk,
        )
        if request.user != booking.skill.owner:
            return HttpResponseForbidden("Only the skill owner may respond.")

        action = request.POST.get("action")
        if action == "accept":
            booking.status = BookingRequest.Status.ACCEPTED
        elif action == "decline":
            booking.status = BookingRequest.Status.DECLINED
        else:
            messages.error(request, "Unknown action.")
            return redirect("skills:dashboard")
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Request {booking.get_status_display().lower()}.")
        return redirect("skills:dashboard")


class SubmitReviewView(LoginRequiredMixin, View):
    """POST /skills/<pk>/review/ — create or update a Review (FR-024)."""

    def post(self, request, pk: int):
        skill = get_object_or_404(Skill, pk=pk)
        if request.user == skill.owner:
            return HttpResponseForbidden("You cannot review your own skill.")

        has_accepted = BookingRequest.objects.filter(
            requester=request.user,
            skill=skill,
            status=BookingRequest.Status.ACCEPTED,
        ).exists()
        if not has_accepted:
            messages.error(request, "Only users with an accepted booking can review.")
            return redirect("skills:detail", pk=skill.pk)

        form = ReviewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please correct the errors in your review.")
            return redirect("skills:detail", pk=skill.pk)

        Review.objects.update_or_create(
            author=request.user,
            skill=skill,
            defaults={
                "rating": form.cleaned_data["rating"],
                "text": form.cleaned_data["text"],
            },
        )
        messages.success(request, "Review saved.")
        return redirect("skills:detail", pk=skill.pk)
