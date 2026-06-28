from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
import os


def serve_frontend(request, path="index.html"):
    if not path or path == "/":
        path = "index.html"
    file_path = os.path.join(str(settings.FRONTEND_DIR), path)
    if not os.path.exists(file_path):
        file_path = os.path.join(str(settings.FRONTEND_DIR), "index.html")
    ext = os.path.splitext(path)[1].lstrip(".")
    ctype = {"css": "text/css", "js": "application/javascript"}.get(ext, "text/html; charset=utf-8")
    with open(file_path, "rb") as f:
        return HttpResponse(f.read(), content_type=ctype)


urlpatterns = [
    path("api/", include("api.urls")),
    path("uploads/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", serve_frontend),
    re_path(r"^(?P<path>[^/]+[.](html|css|js|png|jpg|jpeg|svg|ico))$", serve_frontend),
]
