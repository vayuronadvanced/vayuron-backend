"""
DRF views/viewsets placeholder for the 'core' app.
To be implemented: API views exposing this app's endpoints.
"""

from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Lightweight liveness/readiness check for uptime monitors, the Gunicorn
    systemd unit, and load balancers — see monitoring/health-checks/.

    Checks actual database connectivity (not just "the process is up") since
    a Django process can be running and still be useless if Postgres is
    unreachable. Intentionally does NOT check every dependency (email, etc.)
    — an external monitor should page on this failing; a slow/degraded
    third-party service shouldn't take the whole health check down with it.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({"status": "ok", "database": "ok"}, status=200)
    except OperationalError:
        return Response({"status": "error", "database": "unreachable"}, status=503)
