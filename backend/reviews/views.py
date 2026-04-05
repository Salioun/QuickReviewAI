from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from .models import Reviews
from .serializers import ReviewsPostSerializer, ReviewsSerializer
from .tasks import generate_review_task

class ReviewPostView(APIView):
    def post(self, request):
        serializer = ReviewsPostSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        pr_url = serializer.validated_data['pr_url']

        review = Reviews.objects.create(
            pr_url = pr_url,
            repo_name = '',
            pr_number = 0
        )

        generate_review_task(review.id)

        return Response(
            {'id': review.id, 'status': review.status},
            status=status.HTTP_201_CREATED
        )

class ReviewGetView(APIView):
    def get(self, request, id):
        try:
            review = Reviews.objects.get(pk=id)
        except Reviews.DoesNotExist:
            return Response(
                {'error': 'Review introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ReviewsSerializer(review)
        return Response(serializer.data)
