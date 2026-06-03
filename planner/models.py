from django.db import models

# Project model represents a travel project / Модель проекту представляє туристичную подорож
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

    # Updates project completed status based on its places / Оновлює статус завершеності проекту на основі його місць
    def update_completion_status(self):
        places = self.places.all()
        if not places.exists():
            new_status = False
        else:
            new_status = all(place.visited for place in places)
        
        if self.completed != new_status:
            self.completed = new_status
            self.save(update_fields=['completed'])


# ProjectPlace model represents a place to visit within a project / Модель місця для відвідування в межах проекту
class ProjectPlace(models.Model):
    project = models.ForeignKey(Project, related_name='places', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    visited = models.BooleanField(default=False)

    class Meta:
        unique_together = ('project', 'external_id')
        ordering = ['id']

    def __str__(self):
        return f"{self.title} in {self.project.name}"

    # Recalculates project completion after save / Перераховує статус завершеності проекту після збереження
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.project.update_completion_status()

    # Recalculates project completion after delete / Перераховує статус завершеності проекту після видалення
    def delete(self, *args, **kwargs):
        project = self.project
        super().delete(*args, **kwargs)
        project.update_completion_status()
