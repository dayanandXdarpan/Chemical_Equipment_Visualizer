from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiry to 5 minutes from now
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp}"


class Dataset(models.Model):
    """Model to store uploaded datasets with metadata"""
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='datasets/')
    total_count = models.IntegerField(default=0)
    
    # Dynamic field metadata
    column_structure = models.JSONField(default=dict, blank=True)  # Stores column types and names
    statistics = models.JSONField(default=dict, blank=True)  # Stores calculated statistics
    
    # Legacy fields (kept for backward compatibility)
    avg_flowrate = models.FloatField(default=0.0, null=True, blank=True)
    avg_pressure = models.FloatField(default=0.0, null=True, blank=True)
    avg_temperature = models.FloatField(default=0.0, null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class DynamicData(models.Model):
    """Model to store dynamic data records with flexible structure"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dynamic_records')
    data = models.JSONField()  # Stores all data fields dynamically
    
    def __str__(self):
        return f"Data for {self.dataset.name}"


class Equipment(models.Model):
    """Model to store individual equipment records"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipments')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return self.equipment_name
