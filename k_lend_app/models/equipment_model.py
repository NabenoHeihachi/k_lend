from django.db import models
from k_lend_app.models.account_model import AccountModel

# ---------------------------
# 機材モデル
# 概要：貸出する機材の情報を保持
# ----------------------------
class EquipmentModel(models.Model):
    # 機材ID
    equipment_id = models.CharField(
            verbose_name="機材ID",
            db_column="EQUIPMENT_ID",
            unique=True,
            null=False, 
            blank=False,
            max_length=32,
        )
    
    # 機材名
    equipment_name = models.CharField(
            verbose_name="機材名",
            db_column="EQUIPMENT_NAME",
            null=False, 
            blank=False,
            max_length=48,
        )
    
    # 備考
    remark_text = models.CharField(
            verbose_name="備考",
            db_column="REMARK_TEXT",
            null=False, 
            blank=True,
            default="",
            max_length=256,
        )
    
    # 活性フラグ
    is_active = models.BooleanField(
            verbose_name="活性フラグ", 
            db_column="IS_ACTIVE", 
            null=False, 
            blank=False,
            default=True
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
    created_by = models.ForeignKey(
            AccountModel,
            verbose_name="作成者",
            db_column="CREATED_BY",
            null=True, 
            blank=True,
            on_delete=models.SET_NULL,
            related_name="equipment_created_by"
        )
    
    # 更新時刻
    updated_at = models.DateTimeField(
            verbose_name="更新時刻",
            db_column="UPDATED_AT",
            auto_now=True, 
            null=True, 
            blank=True, 
        )
    
    # 更新者
    updated_by = models.ForeignKey(
            AccountModel,
            verbose_name="更新者",
            db_column="UPDATED_BY",
            null=True, 
            blank=True,
            on_delete=models.SET_NULL,
            related_name="equipment_updated_by"
        )
    
    # テーブル名
    class Meta:
        db_table = "EQUIPMENT_MODEL"
        verbose_name = "機材"
        verbose_name_plural = "機材一覧"
    
    def __str__(self):
        return self.equipment_id + " - " + self.equipment_name
