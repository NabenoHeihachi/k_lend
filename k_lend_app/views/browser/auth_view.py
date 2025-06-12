# ===========================
# ログイン・ログアウトクラス（認証）
# ===========================
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.http import HttpResponseServerError
import pyotp
# メッセージ
from django.contrib import messages
# フォームバリデーションクラス
from k_lend_app.common.validation_function import FormValidationFuncs
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


"""
ログインクラス
"""
class LoginView(TemplateView):

    # テンプレート
    template_name = "k_lend_app/login.html"

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "ログインクラス（認証）"
        # 共通パラメータ
        self.param = {
            "form_error" : False,
            "is_authenticated" : False,
            "user_id" : "",
            "user_password" : "",
            "is_id_password_auth" : False,
            "id_password_term_form_display" : "d-inline",
            "one_time_password_form_display" : "d-none",
        }
    
    def get(self, request, *args, **kwargs):
        """
        GET処理
        """
        # ================
        # 例外処理:START
        # ================
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_GET"].format(self.CLASS_NAME))

            # ログインユーザーがある場合
            if request.user.is_authenticated:
                return redirect("k_lend_app:record_list")

            # データを表示
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
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_POST"].format(self.CLASS_NAME))

            # 文字数
            MIN_LEN = 8
            MAX_LEN = 64

            # リダイレクトURL初期位置
            redirect_url = "k_lend_app:login"

            # ログインユーザーがある場合
            if request.user.is_authenticated:
                return redirect("k_lend_app:record_list")

            # -------------------
            # フォーム名をデータを取得
            # -------------------
            # 入力データ取得
            user_id = request.POST.get("bf_user_id", "")[:MAX_LEN+1]
            user_password = request.POST.get("bf_password", "")[:MAX_LEN+1]
            one_time_password = request.POST.get("bf_one_time_password", "")[:MAX_LEN+1]

            # -------------------------------
            # 入力バリデーション
            # -------------------------------
            def is_valid_input(value):
                return (
                    FormValidationFuncs.is_not_empty(value) and
                    FormValidationFuncs.is_length_valid(value, MIN_LEN, MAX_LEN) and
                    not FormValidationFuncs.has_no_special_characters(value)
                )

            is_valid = (
                is_valid_input(user_id) and
                is_valid_input(user_password)
            )

            if not is_valid:
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["AUTH_FAILED"])

                
            if not is_valid:
                return redirect(redirect_url)

            # -------------------
            # ユーザー認証処理
            # -------------------
            # ユーザー認証
            login_user = authenticate(request=request, username=user_id, password=user_password)

            # <<<<< ログインユーザーがない場合 >>>>>
            if login_user is None:
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["AUTH_FAILED"])
            
            # <<<<< Django管理用アカウントの場合 >>>>>
            elif login_user.is_superuser:
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["ACCOUNT_UNUSABLE"].format("Django管理用のためブラウザからは"))
            
            # <<<<< ログインユーザーがある場合 >>>>>
            else:
                # --------------------
                # 二要素認証が有効な場合
                # --------------------
                if login_user.is_2fa_enabled: 
                    is_input_ctp = request.session.get("is_input_ctp", False)
                    # ワンタイムパスワードの入力が必要な場合
                    fail_count = request.session.get("2fa_fail_count", 0)
                    # ワンタイムパスワードの検証
                    is_ctp_verify = pyotp.TOTP(login_user.two_factor_secret).verify(one_time_password)

                    # <<<<< 失敗回数が3回以上の場合 >>>>>
                    if fail_count >= 3:
                        # セッションを初期化
                        request.session["2fa_fail_count"] = 0
                        request.session["is_input_ctp"] = False
                        # メッセージを表示
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_ONE_TIME_PASSWORD"])
                        # リダイレクト
                        return redirect(redirect_url)

                    # <<<<< ワンタイムパスワード開始かつ、ワンタイムパスワードの検証に失敗した場合 >>>>>
                    if not is_input_ctp or not is_ctp_verify:
                        # ワンタイムパスワード入力かつ、ワンタイムパスワードの検証に失敗した場合
                        if is_input_ctp and not is_ctp_verify:
                            # 失敗回数をカウント
                            request.session["2fa_fail_count"] = fail_count + 1
                            # メッセージを表示
                            messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_ONE_TIME_PASSWORD"])
                        
                        request.session["is_input_ctp"] = True
                        # パラメータを更新
                        self.param.update({
                            "user_id": user_id,
                            "user_password": user_password,
                            "is_id_password_auth": True,
                            "id_password_term_form_display": "d-none",
                            "one_time_password_form_display": "d-inline",
                        })
                        # 表示
                        return self.render_to_response(self.param)
                        
                # ログイン
                login(request, login_user)
                # セッションを初期化
                request.session["2fa_fail_count"] = 0
                request.session["is_input_ctp"] = False

                redirect_url = "k_lend_app:record_list"
                messages.success(request, COMMON_MESSAGE_DICT["BROWSER"]["ACTION_SUCCESS"].format("ログイン"))

            return redirect(redirect_url)
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))
    
"""
ログアウトクラス
"""
class LogoutView(LoginRequiredMixin, TemplateView):

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "ログアウトクラス（認証）"
        # 共通パラメータ
        self.param = {
            "form_error" : False,
        }

    def get(self, request, *args, **kwargs):
        """
        GET処理
        """
        # ================
        # 例外処理:START
        # ================
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_GET"].format(self.CLASS_NAME))

            # メッセージを表示
            messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["PLZ_ACTION"].format("ヘッダーもしくはフッターのボタンから、ログアウト"))
            # リダイレクト
            return redirect("k_lend_app:record_list")
        
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
        try:
            # ログ出力
            logger.info(COMMON_MESSAGE_DICT["LOG"]["VIEW_POST"].format(self.CLASS_NAME))

            # ログアウト
            logout(request)
            # メッセージを表示
            messages.success(request, COMMON_MESSAGE_DICT["BROWSER"]["ACTION_SUCCESS"].format("ログアウト"))
            # リダイレクト
            return redirect("k_lend_app:login")
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))
