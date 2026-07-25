"""
DRF views/viewsets placeholder for the 'core' app.
To be implemented: API views exposing this app's endpoints.
"""

import operator
from functools import reduce

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.blog.models import BlogPost
from apps.careers.models import JobListing

from .serializers import SearchResultSerializer


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


# ─── Global Search ───────────────────────────────────────────────────────
#
# Only covers content that actually lives in the database: published
# BlogPost rows and open JobListing rows. The rest of the site's public
# content — Products, Sectors (+ their sub-applications), Technology,
# About — is hardcoded React/JS on the frontend, not stored here, so it is
# indexed and searched entirely client-side against a build-time-generated
# JSON index (see frontend/scripts/generate-search-index.mjs) and never
# reaches this endpoint at all. This view is deliberately only responsible
# for the two DB-backed sources.

MIN_QUERY_LENGTH = 2
RESULTS_PER_TYPE = 5
SNIPPET_LENGTH = 160


def _snippet(text, length=SNIPPET_LENGTH):
    """Trim on a word boundary rather than mid-word, and never on empty text."""
    text = (text or "").strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "…"


def _build_search_query(query):
    """
    OR-combine each word rather than Django's default AND (plainto_tsquery)
    — a live-typing search dropdown needs "autonomy drone" to still surface
    a document that only mentions "drone", not require every word typed so
    far to be present. SearchRank naturally still favors documents matching
    more of the terms, since it factors in term frequency/coverage.
    """
    terms = [t for t in query.split() if t]
    return reduce(operator.or_, (SearchQuery(t) for t in terms))


def _search_blog_posts(query):
    # Title matches (weight A) rank above body matches (weight B) — see
    # the "search ranking" recommendation from the search feature analysis.
    vector = SearchVector("title", weight="A") + SearchVector("content", weight="B")
    search_query = _build_search_query(query)
    posts = (
        BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)
        .annotate(vector=vector, rank=SearchRank(vector, search_query))
        # Actual full-text match (the `@@` operator), not just "rank > 0" —
        # ts_rank can return a tiny non-zero float even for non-matches, so
        # filtering on rank alone lets unrelated rows leak into results.
        .filter(vector=search_query)
        # Recency as a tiebreaker when relevance scores land close together.
        .order_by("-rank", "-published_at")[:RESULTS_PER_TYPE]
    )
    return [
        {
            "type": "blog",
            "title": post.title,
            "snippet": _snippet(post.excerpt or post.content),
            "url": f"/blog/{post.slug}",
            "score": float(post.rank),
        }
        for post in posts
    ]


def _search_job_listings(query):
    vector = SearchVector("title", weight="A") + SearchVector("description", weight="B")
    search_query = _build_search_query(query)
    listings = (
        # Explicitly filtered to OPEN here rather than relying on the
        # frontend to always pass ?status=open the way JobListingViewSet's
        # default queryset does — search must never be able to leak a
        # closed listing just because a caller forgot a query param.
        JobListing.objects.filter(status=JobListing.Status.OPEN)
        .annotate(vector=vector, rank=SearchRank(vector, search_query))
        .filter(vector=search_query)
        .order_by("-rank")[:RESULTS_PER_TYPE]
    )
    return [
        {
            "type": "careers",
            "title": job.title,
            "snippet": _snippet(job.description),
            "url": f"/careers/{job.slug}",
            "score": float(job.rank),
        }
        for job in listings
    ]


class GlobalSearchView(APIView):
    """
    GET /api/search/?q=... — unified full-text search across published
    blog posts and open job listings. Public/anonymous-readable, same as
    the individual blog/careers list endpoints it draws from.

    Returns {"query": ..., "results": [...]}, results already sorted by
    score across both sources combined (not grouped/paginated per type —
    RESULTS_PER_TYPE caps each source before merging, so the response stays
    small enough for a live-typing dropdown without needing pagination).
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "search"

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) < MIN_QUERY_LENGTH:
            return Response({"query": query, "results": []})

        results = _search_blog_posts(query) + _search_job_listings(query)
        results.sort(key=lambda r: r["score"], reverse=True)

        serializer = SearchResultSerializer(results, many=True)
        return Response({"query": query, "results": serializer.data})
