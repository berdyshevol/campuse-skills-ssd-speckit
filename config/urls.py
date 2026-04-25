from django.contrib import admin
from django.urls import include, path

# URL conventions are defined in specs/001-campus-skillswap/contracts/url-routes.md.
# `django.contrib.auth.urls` supplies login/logout/password reset under /accounts/.
# `accounts.urls` adds /accounts/register/. `skills.urls` is the application root.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("skills.urls")),
]
