from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.base import ContentFile

class CertificateTemplate(models.Model):
    """
    Model for storing certificate templates
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    background = models.ImageField(upload_to='certificate_templates/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Template settings
    font_name = models.CharField(max_length=100, default='Arial')
    font_size = models.PositiveIntegerField(default=60)
    text_color = models.CharField(max_length=7, default='#000000')  # Hex color code
    
    def __str__(self):
        return self.name

class Certificate(models.Model):
    """
    Certificate model for storing certificate information.
    """
    enrollment = models.OneToOneField('courses.Enrollment', on_delete=models.CASCADE, related_name='certificate')
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, 
        blank=True
    )
    file = models.FileField(upload_to='certificates/', null=True, blank=True)
    
    # Additional fields for certificate customization
    custom_text = models.TextField(blank=True, null=True)
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    revocation_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Certificate for {self.enrollment.student.username} - {self.enrollment.course.title}"
        
    @property
    def verification_url(self):
        from django.urls import reverse
        return reverse('verify_certificate', kwargs={'uuid': self.uuid})
