from django.db import models
import os

# Create your models here.

class Document(models.Model):
    """Modelo para almacenar documentos PDF subidos por el usuario"""
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Document {self.id}"

    class Meta:
        ordering = ['-uploaded_at']
