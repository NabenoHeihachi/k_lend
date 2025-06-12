from django.contrib import admin
from k_lend_app.models.account_model import AccountModel
from k_lend_app.models.equipment_model import EquipmentModel
from k_lend_app.models.loan_record_model import LoanRecordModel

@admin.register(AccountModel)
class AccountModelAdmin(admin.ModelAdmin):
    list_display = (
        "username", 
        "type_code",
        "first_name", 
        "last_name",
        "is_2fa_enabled",
    )
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("is_active",)
    ordering = ("-created_at",)

@admin.register(LoanRecordModel)
class LoanRecordModelAdmin(admin.ModelAdmin):
    list_display = (
        "loan_id",
        "borrower_id",
        "borrower_name",
        "equipment",
    )
    search_fields = ("borrower_id", "borrower_name",)
    ordering = ("-start_datetime",)

@admin.register(EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    list_display = (
        "equipment_id",
        "equipment_name",
        "is_active",
    )
    search_fields = ("equipment_name",)
    ordering = ("equipment_name",)