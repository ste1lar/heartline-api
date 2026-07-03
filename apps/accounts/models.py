from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from apps.core.models import TimeStampedModel

# Create your models here.
class UserStatus(models.TextChoices):
    REGISTERED = "REGISTERED", "가입완료"
    VERIFIED = "VERIFIED", "본인인증완료"
    PROFILE_PENDING = "PROFILE_PENDING", "프로필 심사대기"
    PROFILE_REJECTED = "PROFILE_REJECTED", "프로필 반려"
    ACTIVE = "ACTIVE", "정상 이용"
    SUSPENDED = "SUSPENDED", "이용정지"
    WITHDRAWN = "WITHDRAWN", "탈퇴"

class UserManager(BaseUserManager):
    # 이메일 기반 유저 생성 로직

    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email) # 도메인 소문자화 등 정규화
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # 해시로 저장
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("슈퍼유저는 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("슈퍼 유저는 is_superuser=True 여야 합니다.")
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.REGISTERED,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email" # 로그인 식별자 = email
    REQUIRED_FIELDS = [] # createsuperuser가 추가로 물어볼 필드(email/pw는 자동)

    def __str__(self):
        return self.email
