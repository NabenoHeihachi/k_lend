from django.db import models
from k_lend_app.models.account_model import AccountModel
from k_lend_app.models.equipment_model import EquipmentModel

# ---------------------------
# 貸出情報モデル
# 概要：貸出情報を保持
# ----------------------------
class LoanRecordModel(models.Model):
    # 貸出ID
    loan_id = models.AutoField(
            verbose_name="貸出ID",
            db_column="LOAN_ID",
            primary_key=True,
            null=False, 
            blank=False
        )
    
    # 利用者ID
    borrower_id = models.CharField(
            verbose_name="利用者ID",
            db_column="BORROWER_ID",
            max_length=32,
            null=True, 
            blank=True,
            default="",
        )
    
    # 利用者名
    borrower_name = models.CharField(
            verbose_name="利用者名",
            db_column="BORROWER_NAME",
            max_length=48,
        )
    
    # 機材
    equipment = models.ForeignKey(
            EquipmentModel,
            verbose_name="機材",
            db_column="EQUIPMENT",
            null=True, 
            blank=True,
            on_delete=models.SET_NULL,
            related_name="loan_record_equipment",
        )
    
    # 貸出開始日時
    start_datetime = models.DateTimeField(
            verbose_name="貸出開始日時",
            db_column="START_DATETIME",
            null=False, 
            blank=False
        )
    
    # 貸出終了日時
    end_datetime = models.DateTimeField(
            verbose_name="貸出終了日時",
            db_column="END_DATETIME",
            null=True, 
            blank=True
        )
    
    # 備考
    remark_text = models.CharField(
            verbose_name="備考",
            db_column="REMARK_TEXT",
            null=False, 
            blank=True,
            default="",
            max_length=32,
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
            related_name="loan_record_created_by"
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
            related_name="loan_record_updated_by"
        )
    
    # テーブル名
    class Meta:
        db_table = "LOAN_RECORD_MODEL"
        verbose_name = "貸出情報"
        verbose_name_plural = "貸出情報一覧"
    
    def __str__(self):
        return f"ID:{self.loan_id} - {self.borrower_id} - {self.borrower_name} {self.start_datetime}"