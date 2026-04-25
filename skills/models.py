from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Admin-managed taxonomy for skill posts.

    We deliberately avoid `TextChoices` here because FR-028 requires admins
    to add, edit, and retire categories at runtime. A real model gives us a
    `/admin/` page; a `TextChoices` enum would lock the list to deploy time.
    """

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Skill(models.Model):
    """A listing offered by a User."""

    class ContactPreference(models.TextChoices):
        EMAIL = "email", "Email"
        IN_APP = "in_app", "In-app message"
        PHONE = "phone", "Phone"

    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        UNAVAILABLE = "unavailable", "Unavailable"

    title = models.CharField(max_length=120)
    description = models.TextField(max_length=4000)
    # PROTECT prevents a category delete from orphaning posts; admins should
    # retire categories via is_active=False instead.
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="skills",
    )
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    contact_preference = models.CharField(
        max_length=16,
        choices=ContactPreference.choices,
    )
    availability = models.CharField(
        max_length=16,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    # CASCADE: a skill has no meaning without its owner; if an admin deletes
    # the user, their posts go with them.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # FR-014: newest-first listing.
        constraints = [
            # DB-level mirror of the Free/priced rule so admin/shell cannot bypass clean().
            models.CheckConstraint(
                name="skill_free_xor_priced",
                check=(
                    models.Q(is_free=True, price__isnull=True)
                    | models.Q(is_free=False, price__isnull=False, price__gte=0)
                ),
            ),
        ]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("skills:detail", args=[self.pk])

    def clean(self) -> None:
        # Friendly form-level enforcement of the same invariant the CheckConstraint guards.
        if self.is_free:
            self.price = None
        else:
            if self.price is None:
                raise ValidationError({"price": "Priced posts require a price."})
            if self.price < 0:
                raise ValidationError({"price": "Price cannot be negative."})

    @property
    def display_price(self) -> str:
        if self.is_free or self.price is None:
            return "Free"
        return f"${self.price:,.2f}"

    def can_be_booked_by(self, user) -> bool:
        return (
            user.is_authenticated
            and user != self.owner
            and self.availability == self.Availability.AVAILABLE
        )


class BookingRequest(models.Model):
    """A request from one user to engage another user's Skill."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests_made",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="requests",
    )
    message = models.TextField(max_length=2000)
    proposed_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # Defense in depth: clean() rejects bad data at form time, the
        # CheckConstraint stops it at the DB level (admin/shell).
        constraints = [
            models.CheckConstraint(
                name="bookingrequest_status_valid",
                check=models.Q(status__in=["pending", "accepted", "declined"]),
            ),
        ]
        indexes = [
            models.Index(fields=["requester", "status"]),
            models.Index(fields=["skill", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.requester} → {self.skill} ({self.status})"

    def clean(self) -> None:
        if self.requester_id and self.skill_id and self.requester_id == self.skill.owner_id:
            raise ValidationError("You cannot book your own skill.")
        # Only enforce on creation: status changes on existing rows are owner actions.
        if self._state.adding and self.skill_id and self.skill.availability != Skill.Availability.AVAILABLE:
            raise ValidationError("This skill is not currently available for booking.")


class Review(models.Model):
    """A 1–5 star rating + text review.

    The view uses `Review.objects.update_or_create` keyed on (author, skill)
    so a second submission updates the existing row (FR-024) rather than
    raising IntegrityError on the UniqueConstraint below.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # One review per (author, skill); the update_or_create pattern in
            # the view is the user-friendly way to honor this invariant.
            models.UniqueConstraint(
                fields=["author", "skill"],
                name="unique_review_per_author_skill",
            ),
            models.CheckConstraint(
                name="review_rating_range",
                check=models.Q(rating__gte=1, rating__lte=5),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.author} on {self.skill}: {self.rating}★"

    def clean(self) -> None:
        if self.author_id and self.skill_id and self.author_id == self.skill.owner_id:
            raise ValidationError("You cannot review your own skill.")
        if self.author_id and self.skill_id and not BookingRequest.objects.filter(
            requester_id=self.author_id,
            skill_id=self.skill_id,
            status=BookingRequest.Status.ACCEPTED,
        ).exists():
            raise ValidationError("You can only review skills you have an accepted booking for.")
