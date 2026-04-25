from django import forms

from .models import BookingRequest, Category, Review, Skill


class SkillForm(forms.ModelForm):
    """Skill create/edit form. The Free/priced rule is enforced in clean()."""

    class Meta:
        model = Skill
        fields = (
            "title",
            "description",
            "category",
            "is_free",
            "price",
            "contact_preference",
            "availability",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide retired categories from the dropdown.
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        # Bootstrap-friendly widgets for the fields that need explicit input types.
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs["class"] = (existing + " form-check-input").strip()
            elif isinstance(field.widget, (forms.Select,)):
                field.widget.attrs["class"] = (existing + " form-select").strip()
            else:
                field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        is_free = cleaned.get("is_free")
        price = cleaned.get("price")
        if is_free:
            cleaned["price"] = None
        else:
            if price is None:
                self.add_error("price", "Priced posts require a price.")
            elif price < 0:
                self.add_error("price", "Price cannot be negative.")
        return cleaned


class BookingRequestForm(forms.ModelForm):
    """Booking request form. The view stamps requester + skill."""

    class Meta:
        model = BookingRequest
        fields = ("message", "proposed_time")
        widgets = {
            "proposed_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
            ),
            "message": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"},
            ),
        }


class ReviewForm(forms.ModelForm):
    """1–5 rating + text. The view stamps author + skill via update_or_create."""

    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-control", "step": 1},
            ),
            "text": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"},
            ),
        }
