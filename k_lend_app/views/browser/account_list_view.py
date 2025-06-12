# =================================
# アカウント一覧クラス（管理用）
# =================================
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.http import HttpResponseServerError
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
# SQL関連
from django.db.models import Q
from k_lend_app.models.account_model import AccountModel
# フォームバリデーションクラス
from k_lend_app.common.validation_function import FormValidationFuncs
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)

class AccountListView(LoginRequiredMixin, TemplateView):

    # テンプレートファイル
    template_name='k_lend_app/account_list.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "アカウント一覧クラス（管理用）"
        # 共通パラメータ
        self.param = {
            "account_dataset": [],  # アカウント一覧
            "search_form_val": "",
        }

    def get(self, request, *args, **kwargs):
        """
        GET処理
        """
        # ================
        # 例外処理:START
        # ================
        # アクセス権限チェック
        restrict_page_access_by_type_code(request, "職員")
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_GET"].format(self.CLASS_NAME))

            reverse_type_code_dict = {dict_val: dict_key for dict_key, dict_val in COMMON_ACCOUNT_TYPE_CODE.items()}

            if request.user.type_code == COMMON_ACCOUNT_TYPE_CODE["システム管理用"]:
                # データ取得
                account_dataset = AccountModel.objects.all().order_by('-is_active', 'username')
            else:
                account_dataset = AccountModel.objects.filter(username=request.user.username)

            for account_data in account_dataset:
                if account_data.type_code in (COMMON_ACCOUNT_TYPE_CODE["システム管理用"], COMMON_ACCOUNT_TYPE_CODE["貸出情報管理用"],):
                    account_data.is_manageable = True
                else:
                    account_data.is_manageable = False
                    
                if account_data.type_code in list(COMMON_ACCOUNT_TYPE_CODE.values()):
                    # アカウントタイプの表示名を設定
                    account_data.type_code_display = reverse_type_code_dict[account_data.type_code]
                else:
                    # アカウントタイプが不明な場合
                    account_data.type_code_display = "不明"
                # スーパーユーザーの場合
                if account_data.is_superuser:
                    # スーパーユーザーの場合
                    account_data.type_code_display = "Django管理用"

            # データ代入
            self.param["account_dataset"] = account_dataset
            # 表示
            return self.render_to_response(self.param)
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_GET"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))

    def post(self, request, *args, **kwargs):
        """
        POST処理
        """
        # ================
        # 例外処理:START
        # ================
        # アクセス権限チェック
        restrict_page_access_by_type_code(request, "職員")
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_POST"].format(self.CLASS_NAME))

            # -------------------
            # 権限チェック
            # -------------------
            # 管理者権限以外の場合
            if request.user.type_code != COMMON_ACCOUNT_TYPE_CODE["システム管理用"]:
                # 新規作成の場合
                messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["NOT_AUTHORIZED"])
                # リダイレクト
                return redirect('k_lend_app:account_list')

            # -------------------
            # データ取得
            # -------------------
            button_action = request.POST.get('button_action', '')
            account_id = request.POST.get('account_id', '')
            search_form_val = request.POST.get('search_form_val', '').strip()
            
            # ================
            # 有効処理場合
            # ================
            if button_action == "account_change_active":
                # バリデーション結果フラグ
                is_validate_correct = True

                # バリデーション処理
                if not FormValidationFuncs.is_not_empty(account_id):
                    is_validate_correct = False
                # バリデーション処理
                elif not FormValidationFuncs.is_convertible_to_number(account_id):
                    is_validate_correct = False
                    
                # <<<<< エラーがない場合 >>>>>
                if is_validate_correct:
                    try:
                        # 有効更新処理
                        change_active_account = get_object_or_404(AccountModel, id=account_id)
                        change_active_account.is_active = not change_active_account.is_active
                        change_active_account.save()
                        # メッセージ
                        messages.success(request, COMMON_MESSAGE_DICT["DB"]["UPDATE_SUCCESS"].format(f"アカウント（{change_active_account.username}）の有効/無効"))
                        # リダイレクト
                        return redirect('k_lend_app:account_list')
                    except Exception as e:
                        logger.error(COMMON_MESSAGE_DICT["DB"]["UPDATE_ERROR"].format(f"アカウント（{change_active_account.username}）の有効/無効" + str(e)))
                
            # ================
            # 検索処理場合
            # ================
            elif  button_action == "account_search":
                # データ取得
                account_dataset = AccountModel.objects.all()

                # バリデーションフラグ
                is_validate_correct = True

                # バリデーション
                if search_form_val:
                    if not FormValidationFuncs.is_length_valid(search_form_val, 1, 32):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format("検索文字列", 1, 32))
                    elif FormValidationFuncs.has_no_special_characters(search_form_val):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format("検索文字列"))

                if is_validate_correct:
                    account_dataset = account_dataset.filter(
                        Q(username__icontains=search_form_val) |
                        Q(email__icontains=search_form_val) |
                        Q(first_name__icontains=search_form_val) |
                        Q(last_name__icontains=search_form_val)
                    )

                    # データ代入
                    self.param["account_dataset"] = account_dataset
                    self.param["search_form_val"] = search_form_val

                    # 表示
                    return self.render_to_response(self.param)
                else:
                    return redirect('k_lend_app:account_list')

            # ==============================
            # ボタンアクションに該当がない場合
            # ==============================
            messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["INVALIDF_REQUEST"])
            return redirect('k_lend_app:account_list')
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))