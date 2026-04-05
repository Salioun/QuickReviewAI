from django.test import TestCase
from unittest.mock import patch, MagicMock
from .services import GithubService
from .models import Reviews

class GitHubServiceParseTest(TestCase):
    def setUp(self):
        self.service = GithubService(token='fake-token')

    def test_parse_url_valide(self):
        result = self.service.parse_url(
            'https://github.com/Salioun/test-python-app/pull/42'
        )
        self.assertEqual(result['owner'],'Salioun')
        self.assertEqual(result['repo'],'test-python-app')
        self.assertEqual(result['number'], 42)
    
    def test_parse_url_invalid(self):
        with self.assertRaises(ValueError):
            self.service.parse_url('https://github.com/no-pr')

class ReviewModelTest(TestCase):
    """
    Tests pour le model Review.
    """

    def test_creation_review(self):
        review = Reviews.objects.create(
            pr_url='https://github.com/owner/repo/pull/1',
            repo_name='owner/repo',
            pr_number=1,
        )
        self.assertEqual(review.status, Reviews.Status.PENDING)
        self.assertEqual(review.result_text, '')
        self.assertIsNone(review.score)

    def test_str_representation(self):
        review = Reviews.objects.create(
            pr_url='https://github.com/owner/repo/pull/1',
            repo_name='owner/repo',
            pr_number=1,
        )
        self.assertIn('owner/repo', str(review))