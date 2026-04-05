from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from .models import Reviews

#Serializer for the POST
class ReviewsPostSerializer(serializers.Serializer):
    pr_url = serializers.URLField()

    def validate_pr_url(self, value):
        if 'github.com' not in value or '/pull' not in value:
            raise serializers.ValidationError(
                "L'URL doit être un pull request Github "
                "(ex: https://github.com/owner/repo/pull/123)"
            )

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = [
            'id',
            'pr_url',
            'repo_name',
            'pr_number',
            'status',
            'result_text',
            'score',
            'created_at',
        ]