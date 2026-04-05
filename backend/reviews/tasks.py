import logging
from celery import shared_task
from django.conf import settings
from .models import Reviews
from .services import GithubService

logger = logging.getLogger(__name__)

@shared_task
def generate_review_task(review_id: int):
    try:
        review = Reviews.objects.get(id=review_id)
        review.status = Reviews.Status.PROCESSING
        review.save()
        
        github = GithubService(token=settings.GITHUB_TOKEN)
        pr_data = github.get_pr_diff(review.pr_url)

        logger.info(
            f"Diff récupéré pour {pr_data['repo_name']} "
            f"#{pr_data['number']} — "
            f"{len(pr_data['diff'])} caractères"
        )

        review.result_text = f"Diff récupéré : {pr_data['files_count']} fichiers modifiés"
        review.status = Reviews.Status.COMPLETED
        review.save()

    except Reviews.DoesNotExist:
        logger.error(f"f Review {review_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors de la review {review_id} : {e}")
        review.status = Reviews.Status.FAILED
        review.save()    
