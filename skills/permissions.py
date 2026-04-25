from django.http import HttpResponseForbidden


class OwnerOnlyMixin:
    """Reject the request unless `request.user` owns the object.

    Preferred over `UserPassesTestMixin` because the intent reads at a glance
    and the implementation lives in ten lines.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            return HttpResponseForbidden("You do not own this skill.")
        return super().dispatch(request, *args, **kwargs)
