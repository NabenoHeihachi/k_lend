from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
import pyotp

# ---------------------------
# アカウントテーブル
# 概要：システムログイン用アカウントを保持
# ----------------------------
class AccountModel(AbstractUser):
    # ユーザーID
    username = models.CharField(
            verbose_name="ユーザーID",
            db_column="USER_ID",
            max_length=32, 
            unique=True, 
            null=False,
            blank=False,
            validators=[RegexValidator(r'^[A-Za-z0-9]{8,32}$')],
        )
    
    # Eメール
    email = models.EmailField(
            verbose_name="Eメール",
            db_column="EMAIL",
            max_length=254, 
            unique=True, 
            null=True,
            blank=True
        )
    
    # 名前
    first_name = models.CharField(
            verbose_name="名前",
            db_column="FIRST_NAME",
            max_length=64, 
            null=False,
            blank=False
        )
    
    # 苗字
    last_name = models.CharField(
            verbose_name="苗字",
            db_column="LAST_NAME",
            max_length=64, 
            null=False,
            blank=False
        )
    
    # アカウントタイプ
    type_code = models.CharField(
            verbose_name="タイプコード",
            db_column="TYPE_CODE",
            choices=[
                (code, name) for name, code in COMMON_ACCOUNT_TYPE_CODE.items()
            ],
            default="9999",
            max_length=32, 
            null=False,
            blank=False,
        )
    
    # 2faの有効フラグ
    is_2fa_enabled = models.BooleanField(
            verbose_name="2FAの有効フラグ",
            db_column="IS_2FA_ENABLED",
            default=False,
            null=False,
            blank=False
        )
    
    # 2faのシークレットキー
    two_factor_secret = models.CharField(
            verbose_name="2FAのシークレットキー",
            db_column="TWO_FACTOR_SECRET",
            max_length=32, 
            null=True,
            blank=True
        )
    
    # 作成時刻
    created_at = models.DateTimeField(
            verbose_name="作成時刻",
            db_column="CREATED_AT",
            auto_now_add=True,
            null=False, 
            blank=False
        )
    
    # 作成者
    created_by = models.CharField(
            verbose_name="作成者",
            db_column="CREATED_BY",
            max_length=64,
            null=False,
            blank=False
        )
    
    # 更新時刻
    updated_at = models.DateTimeField(
            verbose_name="更新時刻",
            db_column="UPDATED_AT",
            auto_now=True, 
            null=True,
            blank=False
        )
    
    # 更新者
    updated_by = models.CharField(
            verbose_name="更新者",
            db_column="UPDATED_BY",
            max_length=32,
            null=True,
            blank=False
        )
    
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def save(self, *args, **kwargs):
        if not self.two_factor_secret:
            self.two_factor_secret = pyotp.random_base32()
        super().save(*args, **kwargs)

    # テーブル名
    class Meta:
        db_table = "ACCOUNT_MODEL"
        verbose_name = "アカウント"
        verbose_name_plural = "アカウント一覧"

    