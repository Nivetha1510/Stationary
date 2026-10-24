import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()

# Django does not serve uploaded/seeded media when DEBUG is off, so let WhiteNoise serve the
# read-only media folder (product, team and trending images) that ships with the deployment.
from django.conf import settings  # noqa: E402
from whitenoise import WhiteNoise  # noqa: E402

if os.path.isdir(settings.MEDIA_ROOT):
    application = WhiteNoise(application, root=settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
