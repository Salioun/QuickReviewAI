from django.test import TestCase
from unittest.mock import patch, MagicMock
from .services import GithubService, LLMService
from .models import Reviews
import json
#python3 manage.py test reviews

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

class LLMServiceTest(TestCase):
    def setUp(self):
        self.service = LLMService(api_key='fake-api-key')
    
    def _make_mock_response(self, json_str: str):
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json_str
        mock_response.content = [mock_content]
        return mock_response    

    @patch('reviews.services.anthropic.Anthropic')
    def test_generate_review_valid_json(self, mock_anthropic):
        fake_json = json.dumps({
            "score": 7,
            "summary": "Bon PR dans l'ensemble.",
            "bugs": [],
            "suggestions": [],
            "performance": [],
            "positive_points": ["Code clair"]
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = self._make_mock_response(fake_json)
        mock_anthropic.return_value = mock_client


        pr_data = {
            'repo_name': 'owner/repo',
            'number': 1,
            'title': 'Test PR',
            'description': '',
            'files_count': 2,
            'diff': 'diff --git a/file.py\n+print("hello")',
        }
        service = LLMService(api_key='fake-api-key')
        result = service.generate_review(pr_data)

        self.assertEqual(result['score'], 7)
        self.assertEqual(result['summary'], "Bon PR dans l'ensemble.")
        self.assertIsInstance(result['bugs'], list)
    
    @patch('reviews.services.anthropic.Anthropic')
    def test_generate_review_json_invalide(self, mock_anthropic_class):
        """Si le LLM retourne du texte invalide → ValueError."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = self._make_mock_response(
            "Désolé, je ne peux pas analyser ce diff."
        )
        mock_anthropic_class.return_value = mock_client

        pr_data = {
            'repo_name': 'owner/repo', 'number': 1,
            'title': 'Test', 'description': '', 'files_count': 1,
            'diff': 'diff',
        }

        service = LLMService(api_key='fake-api-key')

        with self.assertRaises(ValueError):
            service.generate_review(pr_data)

    def test_truncate_diff_court(self):
        """Un diff court n'est pas tronqué."""
        diff = "a" * 1000
        result = self.service._truncate_diff(diff)
        self.assertEqual(result, diff)

    def test_truncate_diff_long(self):
        """Un diff trop long est tronqué avec un message."""
        diff = "a" * 20_000
        result = self.service._truncate_diff(diff)
        self.assertIn("tronqué", result)
        self.assertLess(len(result), 20_000)