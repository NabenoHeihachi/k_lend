# =================================
# ブラウザ関連のURL設定
# =================================
from django.urls import path
from k_lend_app.views.browser.auth_view import LoginView, LogoutView
# 貸出記録関連
from k_lend_app.views.browser.record_list_view import RecordListView
from k_lend_app.views.browser.record_form_view import RecordFormView
from k_lend_app.views.browser.record_download_view import RecordDownloadView
# 機材関連
from k_lend_app.views.browser.equipment_list_view import EquipmentListView
from k_lend_app.views.browser.equipment_form_view import EquipmentFormView
from k_lend_app.views.browser.equipment_download_view import EquipmentDownloadView
from k_lend_app.views.browser.equipment_qrcode_view import EquipmentQRCodeView
# アカウント関連
from k_lend_app.views.browser.account_list_view import AccountListView
from k_lend_app.views.browser.account_2fa_view import Account2FASettingView
from k_lend_app.views.browser.account_form_view import AccountFormView
# ドキュメント関連
from k_lend_app.views.browser.documents_view import DocumentView

urlpatterns = [
    # 認証関連
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 貸出記録関連
    path('', RecordListView.as_view(), name='record_list'),
    path('records/create/', RecordFormView.as_view(), name='record_create'),
    path('records/<int:loan_id>/edit/', RecordFormView.as_view(), name='record_edit'),
    path('records/download/', RecordDownloadView.as_view(), name='record_download'),

    # 機材管理関連
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', EquipmentFormView.as_view(), name='equipment_create'),
    path('equipment/<int:model_id>/edit/', EquipmentFormView.as_view(), name='equipment_edit'),
    path('equipment/download/', EquipmentDownloadView.as_view(), name='equipment_download'),
    path('equipment/<int:model_id>/qrcode/', EquipmentQRCodeView.as_view(), name='equipment_qrcode'),

    # アカウント管理関連
    path('account/', AccountListView.as_view(), name='account_list'),
    path('account/create/', AccountFormView.as_view(), name='account_create'),
    path('account/<int:account_id>/edit/', AccountFormView.as_view(), name='account_edit'),
    path('account/2fa-setting/', Account2FASettingView.as_view(), name='account_2fa'),
    
    # ドキュメント関連
    path('document/<str:document_type>/', DocumentView.as_view(), name='document'),

]