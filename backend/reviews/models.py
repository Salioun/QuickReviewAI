from django.db import models

# Create your models here.
class Reviews(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PROCESSING = 'processing', 'En cours'
        COMPLETED = 'completed', 'Terminée'
        FAILED = 'failed', 'Échouée'

    pr_url = models.URLField()
    repo_name = models.CharField(max_length=200)
    pr_number = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    result_text = models.TextField(blank=True, default='')
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.repo_name} #{self.pr_number} — {self.status}"



