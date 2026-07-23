import logging
from celery import shared_task
from django.conf import settings
from .models import Reviews
from .services import GithubService, LLMService

logger = logging.getLogger(__name__)

@shared_task
def generate_review_task(review_id: int):
    try:
        review = Reviews.objects.get(id=review_id)
        review.status = Reviews.Status.PROCESSING
        review.save()
        
        # Récupération du diff du PR
        logger.info(f"Review {review_id} : Récupération du diff pour {review.pr_url}")
        github = GithubService(token=settings.GITHUB_TOKEN)
        pr_data = github.get_pr_diff(review.pr_url)

        review.repo_name = pr_data['repo_name']
        review.pr_number = pr_data['number']
        review.save()

        logger.info(
            f"[Review {review_id}] Diff récupéré — "
            f"{pr_data['files_count']} fichiers, "
            f"{len(pr_data['diff'])} caractères"
        )
        # Génération de la review
        logger.info(f"[Review {review_id}] Génération de la review")
        llm = LLMService(api_key=settings.ANTHROPIC_API_KEY)
        review_data = llm.generate_review(pr_data)

        review.result_json = review_data
        review.score = review_data.get('score', None)
        review.result_text = review_data.get('summary', '')
        review.status = Reviews.Status.COMPLETED
        review.save()
        logger.info(f"[Review {review_id}] Review générée avec succès"
            f"Score : {review.score}"
        )

    except Reviews.DoesNotExist:
        logger.error(f"[Review {review_id}] Review introuvable")

    except ValueError as e:
        logger.error(f"[Review {review_id}] Erreur lors de la génération de la review : {e}")
        if review:
            review.status = Reviews.Status.FAILED
            review.save()

    except Exception as e:
        logger.error(f"[Review {review_id}] Erreur lors de la génération de la review : {e}")
        if review:
            review.status = Reviews.Status.FAILED
            review.result_text = f"Erreur interne : {type(e).__name__}"
            review.save()