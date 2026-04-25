from django.urls import path

from . import views

app_name = "skills"

urlpatterns = [
    path("", views.SkillListView.as_view(), name="list"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("skills/new/", views.SkillCreateView.as_view(), name="create"),
    path("skills/<int:pk>/", views.SkillDetailView.as_view(), name="detail"),
    path(
        "skills/<int:pk>/request/",
        views.RequestBookingView.as_view(),
        name="request_booking",
    ),
    path(
        "requests/<int:pk>/respond/",
        views.RespondRequestView.as_view(),
        name="respond_request",
    ),
    path(
        "skills/<int:pk>/review/",
        views.SubmitReviewView.as_view(),
        name="submit_review",
    ),
    path(
        "skills/<int:pk>/edit/",
        views.SkillUpdateView.as_view(),
        name="update",
    ),
    path(
        "skills/<int:pk>/delete/",
        views.SkillDeleteView.as_view(),
        name="delete",
    ),
]
