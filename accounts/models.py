from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
# from django.contrib.auth.models import User

# module for super admin


class MyAccountManager(BaseUserManager):
    # For creating  normal user
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('You must have an email address!')

        if not username:
            raise ValueError('You must have an username!')

        user = self.model(
            # small letter from capital letter using normalize
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,

        )

        # set password for setting password which is in build function
        user.set_password(password)
        user.save(using=self._db)
        return user

    # For creating superuser
    # here using create_superuser for using above create_superuser method
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,

            # these are the parameters accepted by create_user methon
        )

        # to set all the permmission to True
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=40)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='user_profile')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return self.address_line_1
