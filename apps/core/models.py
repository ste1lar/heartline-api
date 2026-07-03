from django.db import models

# Create your models here.
class TimeStampedModel(models.Model):
    # 생성/수정 시각을 자동 기록하는 추상 베이스
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # 이 모델 자체는 테이블 안 만듦

class SoftDeleteModel(models.Model):
    # 실제 삭제 대신 플래그로 지우는 추상 베이스
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
