# =================================
# アカウント設定クラス（管理用）
# =================================
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.http import HttpResponseServerError
# フォームバリデーションクラス
from k_lend_app.common.validation_function import FormValidationFuncs
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
import qrcode
import pyotp
import base64
from io import BytesIO
# ログ
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

class AccountSettingView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "アカウント証設定クラス（管理用）"

    # テンプレートファイル
    template_name = 'k_lend_app/account_setting.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.param = {
            "account": None,  # アカウントデータ
            "qrcode_base64_str": None,  # QRコード画像
            
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

            # ワンタイムパスワードの生成に使う秘密鍵を取得
            two_factor_secret_key = request.user.two_factor_secret

            if request.user.is_2fa_enabled == False:
                # 二要素認証が有効な場合、QRコードを生成するための秘密鍵を取得
                two_factor_secret_key = request.user.two_factor_secret

                # TOTPインスタンスを作成（Time-based One-Time Password）
                totp_instance = pyotp.TOTP(two_factor_secret_key)

                # QRコードに埋め込むURL形式のプロビジョニングURIを作成
                totp_provision_uri_str = totp_instance.provisioning_uri(
                    name=f"{request.user.username}",
                    issuer_name="K-LEND 貸出管理システム"
                )

                # QRコードを画像として生成
                qr_code_image_obj = qrcode.make(totp_provision_uri_str)

                # PNG画像としてメモリに保存するためのバッファを用意
                memory_image_buffer = BytesIO()
                qr_code_image_obj.save(memory_image_buffer, format="PNG")

                # メモリ上のPNG画像をbase64にエンコード（HTMLで埋め込めるように）
                png_binary_data = memory_image_buffer.getvalue()
                png_base64_bytes = base64.b64encode(png_binary_data)
                png_base64_str = png_base64_bytes.decode("utf-8")

                self.param["qrcode_base64_str"] = png_base64_str

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
            # データ取得
            # -------------------
            button_action = request.POST.get('button_action', '')
            bf_one_time_token = request.POST.get('bf_one_time_token', '')
            bf_new_password = request.POST.get('bf_new_password', '')
            bf_new_password_confirm = request.POST.get('bf_new_password_confirm', '')

            # --------------------
            # データチェック
            # --------------------
            # ボタンアクションのチェック
            if button_action not in ["change_password", "enable_2fa", "disable_2fa"]:
                # メッセージ出力
                messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["INVALID_REQUEST"])
                # リダイレクト
                return redirect("k_lend_app:account_setting")
            
            # ------------------------
            # パスワード更新の場合
            # ------------------------
            if button_action == "change_password":
                # パスワードバリデーション
                if not FormValidationFuncs.is_match(bf_new_password, "password"):
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["RE_PASSWORD"])
                    return redirect("k_lend_app:account_setting")
                # パスワードの一致チェック
                if bf_new_password != bf_new_password_confirm:
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PASSWORD_CONFIRM"])
                    return redirect("k_lend_app:account_setting")

                # パスワードの更新処理
                request.user.set_password(bf_new_password)
                request.user.save(update_fields=["password"])
                messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format("新しいパスワード"))
                return redirect("k_lend_app:account_setting")

            # ------------------------
            # 二要素認証の有効化する場合
            # ------------------------
            if button_action == "enable_2fa":
                # 二要素認証を有効にする場合
                # ワンタイムパスワードの生成に使う秘密鍵を取得
                two_factor_secret_key = request.user.two_factor_secret

                # TOTPインスタンスを作成（Time-based One-Time Password）
                totp_instance = pyotp.TOTP(two_factor_secret_key)

                # ワンタイムトークンの検証
                if not totp_instance.verify(bf_one_time_token):
                    # メッセージ出力
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_ONE_TIME_PASSWORD"])
                    # リダイレクト
                    return redirect("k_lend_app:account_setting")

                try:
                    # 二要素認証を有効にする
                    request.user.is_2fa_enabled = True
                    # 保存
                    request.user.save(update_fields=["is_2fa_enabled"])
                    # メッセージ出力
                    messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format("二要素認証の有効化"))
                except Exception as e:
                    logger.error(COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("二要素認証の有効化") + str(e))
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("二要素認証の有効化"))
            # -------------------------
            # 二要素認証を無効にする場合
            # -------------------------
            elif button_action == "disable_2fa":
                try:
                    # 二要素認証を無効にする
                    request.user.is_2fa_enabled = False
                    # 保存
                    request.user.save(update_fields=["is_2fa_enabled"])
                    # メッセージ出力
                    messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format("二要素認証の無効化"))
                except Exception as e:
                    logger.error(COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("二要素認証の無効化") + str(e))
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("二要素認証の無効化"))

            # リダイレクト
            return redirect("k_lend_app:account_setting")
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))