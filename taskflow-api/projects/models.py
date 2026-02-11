from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Project(models.Model):
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('archivado', 'Archivado'),
        ('en_pausa', 'En Pausa'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects_as_member', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='activo')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 2

            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1

            self.slug = slug
        super().save(*args, **kwargs)
