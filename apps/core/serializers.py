"""
DRF serializers placeholder for the 'core' app.
To be implemented: serializers for REST API request/response payloads.
"""

from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    """
    Normalized shape every /api/search/ result is coerced into, regardless
    of which model it came from (BlogPost, JobListing, ...) — the frontend
    renders a single result-row component off of this shape rather than
    branching per source type.
    """

    type = serializers.CharField()
    title = serializers.CharField()
    snippet = serializers.CharField()
    url = serializers.CharField()
    score = serializers.FloatField()

