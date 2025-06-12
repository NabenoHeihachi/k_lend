# =================================
# アカウントフォームクラス（管理用）
# =================================
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.http import HttpResponseServerError, HttpResponseNotFound
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import Http404
# SQL関連
from k_lend_app.models.account_model import AccountModel
# フォームバリデーションクラス
from k_lend_app.common.validation_function import FormValidationFuncs
# ログ
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

class AccountFormView(LoginRequiredMixin, TemplateView):

    # テンプレートファイル
    template_name = 'k_lend_app/account_form.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "アカウントフォームクラス（管理用）"
        self.param = {
            "account": None,  # アカウントデータ
            "is_show_detail": False,  # 編集画面フラグ
            "account_type_code_dict": COMMON_ACCOUNT_TYPE_CODE,  # アカウントタイプコード辞書
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

            # アカウントDB ID初期値
            account_id = None

            # -------------------
            # アカウント情報取得
            # -------------------
            # URLにIDがある場合
            if "account_id" in kwargs:
                # IDを取得
                account_id = kwargs["account_id"]
                # データを取得
                account_data = None
                try:
                    account_data = get_object_or_404(AccountModel, pk=account_id)
                except Http404:
                    return HttpResponseNotFound(render(request, '404.html'))
                
                if account_data:
                    self.param["account"] = account_data
                    # 編集画面フラグをTrueに
                    self.param["is_show_detail"] = True

                    if request.user.type_code != COMMON_ACCOUNT_TYPE_CODE["システム管理用"] and request.user.username != account_data.username:
                        return HttpResponseNotFound(render(request, '404.html'))

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

            # アカウントDB ID初期値
            account_id = None
            # 詳細フラグ
            is_show_detail = False
            # バリデーション結果フラグ
            is_validate_correct = True
            # パスワード更新の有無
            is_update_password = False

            # POSTデータ値辞書初期値
            post_val_dict = {}

            # 全フォーム名リスト
            FORM_NAME_LIST = ["username", "type_code", "first_name", "last_name", "password", "confirm", "email"]
            # POSTフォーム値定義辞書
            POST_FORM_DEF_DICT = {
                "first_name":{"name":"名前", "max":64, "min":1}, 
                "last_name":{"name":"苗字", "max":64, "min":1}, 
                }

            # -------------------
            # POSTタイプ識別
            # -------------------
            # URLにIDがある場合
            if "account_id" in kwargs:
                # IDを取得
                account_id = kwargs["account_id"]
                # 編集画面フラグをTrueに
                self.param["is_show_detail"] = True
                # 詳細フラグ
                is_show_detail = True

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
            # フォームデータ取得
            # -------------------
            # リストでループ
            for form_name in FORM_NAME_LIST:
                # フォーム値取得
                post_val_dict[form_name] = request.POST.get(form_name, "").strip()

            # -------------------
            # データバリデーション
            # -------------------
            # 更新かつパスワード入力の場合
            if is_show_detail and (FormValidationFuncs.is_not_empty(post_val_dict["password"]) or FormValidationFuncs.is_not_empty(post_val_dict["confirm"])):
                    is_update_password = True
            
            for text_form in POST_FORM_DEF_DICT:
                # フォームデータ辞書
                from_def_dict = POST_FORM_DEF_DICT[text_form]
                # 長さチェック
                if not FormValidationFuncs.is_length_valid(post_val_dict[text_form], from_def_dict["min"], from_def_dict["max"] ):
                    # バリデーションフラグ更新
                    is_validate_correct = False
                    # 日本語フォーム名
                    text_form_jp = POST_FORM_DEF_DICT[text_form]["name"]
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format(text_form_jp, from_def_dict["min"], from_def_dict["max"]))
                # 入力値チェック
                if FormValidationFuncs.has_no_special_characters(post_val_dict[text_form]):
                    # バリデーションフラグ更新
                    is_validate_correct = False
                    # 日本語フォーム名
                    text_form_jp = POST_FORM_DEF_DICT[text_form]["name"]
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format(text_form_jp))
                
            if not FormValidationFuncs.is_match(post_val_dict["username"], "user_id"):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["RE_USER_ID"])
            
            if not FormValidationFuncs.is_match(post_val_dict["password"], "password"):
                if not is_show_detail and not is_update_password:
                    # バリデーションフラグ更新
                    is_validate_correct = False
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["RE_PASSWORD"])
                
            if post_val_dict["email"] != "" and not FormValidationFuncs.is_match(post_val_dict["email"], "email"):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP_EMAIL"].format("メールアドレス"))

            if post_val_dict["type_code"] not in list(COMMON_ACCOUNT_TYPE_CODE.values()):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_SELECT"].format("権限タイプ"))
            
            if post_val_dict["password"] != post_val_dict["confirm"]:
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PASSWORD_CONFIRM"].format("パスワード"))

            # -------------------
            # DB登録
            # -------------------
            # バリデーションエラーがない場合
            if is_validate_correct:
                try:
                    # 新規作成の場合
                    if is_show_detail == False:
                        # モデル取得
                        account_model = AccountModel()
                    # 更新の場合
                    else:
                        # モデル取得
                        account_model = get_object_or_404(AccountModel, pk=account_id)

                    # 更新
                    account_model.username = post_val_dict["username"]
                    account_model.type_code = post_val_dict["type_code"]
                    account_model.first_name = post_val_dict["first_name"]
                    account_model.last_name = post_val_dict["last_name"]
                    account_model.updated_by = request.user.username
                    account_model.is_superuser = False
                    account_model.is_staff = False
                    # メールアドレスがある場合
                    if post_val_dict["email"]:
                        account_model.email = post_val_dict["email"]
                    elif is_show_detail:
                        account_model.email = None
                    
                    # パスワードがある場合
                    if post_val_dict["password"]:
                        account_model.password = make_password(post_val_dict["password"])
                    # 新規作成の場合
                    if is_show_detail == False:
                        account_model.created_by = request.user.username
                    # 変更の保存
                    account_model.save()

                    # メッセージ表示
                    new_user_id = post_val_dict["username"]
                    messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format(f"アカウント情報（ID:{new_user_id}）"))

                    # リダイレクト
                    if is_show_detail and account_id:
                        return redirect('k_lend_app:account_edit', account_id=account_id)
                    
                    return redirect('k_lend_app:account_list')
                
                # ユーニーク制約違反の場合
                except IntegrityError:
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["ALREADY_REGISTERED"].format("ユーザーIDまたはメールアドレス"))

                except Exception as e:
                    logger.error(COMMON_MESSAGE_DICT["DB"]["UPDATE_ERROR"].format("アカウント情報") + str(e))
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["UPDATE_ERROR"].format("アカウント情報"))
                
            # リダイレクト
            if is_show_detail and account_id:
                return redirect('k_lend_app:account_edit', account_id=account_id)
            
            return redirect('k_lend_app:account_create')
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))