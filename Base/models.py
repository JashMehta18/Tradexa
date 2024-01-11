from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from PIL import Image
# Create your models here.
class news(models.Model):
	headlines = models.CharField(max_length=255, null=False, primary_key=True)
	link = models.CharField(max_length=255, null=False)
	img_url = models.CharField(max_length=255, null=False)
	date = models.DateTimeField(default=timezone.now)

class UserAccount(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	pro_Account = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username
		
# Create your models here.
class StockDetail(models.Model):
    stock = models.CharField(max_length=255, unique=True)
    user = models.ManyToManyField(User)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	# image = models.ImageField(default='avatar7.png', upload_to='profile_pics/')
	image = models.ImageField(default='avatar7.png', upload_to='profile_pics/')
	phone_number = models.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
							message="Phone number must be entered in the format: '+919800220022'. Upto 13 digits allowed.")],
							max_length=13, blank=True) # validators should be a list

	street = models.CharField(validators=[RegexValidator(message='e.g. 14th street')], max_length=255,blank=True)
	city = models.CharField(validators=[RegexValidator(message='e.g. Mumbai')], max_length=255, blank=True)
	state = models.CharField(validators=[RegexValidator(message='e.g. Maharashtra')], max_length=255, blank=True)
	zip = models.CharField(validators=[RegexValidator(regex=r'^\d{6}$',
							message="Phone number must be entered in the format: '+919800220022'. Upto 13 digits allowed.")],
							max_length=6, blank=True)

	def __str__(self):
		return f'{self.user.username} Profile'

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		img = Image.open(self.image.path)

		if img.height > 200 or img.width > 200:
			output_size = (200, 200)
			img.thumbnail(output_size)
			img.save(self.image.path)