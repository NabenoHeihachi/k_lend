# =================================
# カスタムコマンド: ユーザー作成
# =================================
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from k_lend_app.models.account_model import AccountModel
from k_lend_app.common.validation_function import FormValidationFuncs
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
import getpass

class Command(BaseCommand):
    help = "新規ユーザーを作成します"

    def handle(self, *args, **options):
        """
        新規作成ユーザー作成処理
        """
        # ================
        # 例外処理:START
        # ================
        try:
            # -----------------
            # ユーザー情報の取得
            # -----------------
            input_user_id = input(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP"].format('ユーザーID'))
            input_password = getpass.getpass(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP_HID"].format('パスワード'))
            input_confirm = getpass.getpass(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP_HID"].format('パスワード（確認用）'))
            input_type_code = input(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP"].format('タイプコード') + COMMON_MESSAGE_DICT["COMMAND"]["ACCOUNT_TYPE_CHOICES"]+ ": ")
            input_last_name = input(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP"].format('苗字'))
            input_first_name = input(COMMON_MESSAGE_DICT["COMMAND"]["PLZ_INP"].format('名前'))
            
            # -------------------
            # データバリデーション
            # -------------------
            # <<<<< ユーザーID >>>>>
            if not FormValidationFuncs.is_match(input_user_id, "user_id"):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["RE_USER_ID"])
            # <<<<< パスワード >>>>>
            if not FormValidationFuncs.is_match(input_password, "password"):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["RE_PASSWORD"])
            if input_password != input_confirm:
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PASSWORD_CONFIRM"])
            # <<<<< ユーザータイプコード >>>>>>
            if input_type_code not in list(COMMON_ACCOUNT_TYPE_CODE.values()):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_SELECT"].format('タイプコード') + COMMON_MESSAGE_DICT["COMMAND"]["ACCOUNT_TYPE_CHOICES"])
            # <<<<< 名前 >>>>>
            # ***空値チェック***
            if FormValidationFuncs.is_not_empty(input_last_name) == False:
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format('苗字', '1', '64'))
            if FormValidationFuncs.is_not_empty(input_first_name) == False:
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format('名前', '1', '64'))
            # ***長さチェック***
            if not FormValidationFuncs.is_length_valid(input_last_name, 1, 64):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format('苗字', '1', '64'))
            if not FormValidationFuncs.is_length_valid(input_first_name, 1, 64):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format('名前', '1', '64'))
            # ***入力値チェック***
            if FormValidationFuncs.has_no_special_characters(input_last_name):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format('苗字'))
            if FormValidationFuncs.has_no_special_characters(input_first_name):
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format('名前'))
            

            # -------------------
            # 確認
            # -------------------
            input_is_correct = input(COMMON_MESSAGE_DICT["COMMAND"]["CFM_CREATE"].format('上記の内容でユーザーを'))
            if input_is_correct.lower() != 'y':
                # キャンセル
                print(COMMON_MESSAGE_DICT["COMMAND"]["ACTION_CANCEL"].format('ユーザー作成'))
                return
            
            # -------------------
            # DB登録
            # -------------------
            try:
                # モデル取得
                account_model = AccountModel()
                # ユーザーIDの重複チェック
                account_model.username = input_user_id
                account_model.type_code = input_type_code
                account_model.first_name = input_first_name
                account_model.last_name = input_last_name
                account_model.created_by = "SERVER_COMMAND"
                account_model.updated_by = "SERVER_COMMAND"
                account_model.is_superuser = False
                account_model.is_staff = False
                account_model.password = make_password(input_password)
                # 変更の保存
                account_model.save()

            except IntegrityError:
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_INPUT"].format('ユーザーID'))
                return

            except Exception as e:
                # コマンドエラー
                raise CommandError(COMMON_MESSAGE_DICT["COMMAND"]["SAVE_ERROR"].format("", e))
                return

            # メッセージ表示
            self.stdout.write(
                self.style.SUCCESS(COMMON_MESSAGE_DICT["COMMAND"]["ACTION_SUCCESS"].format('ユーザー作成'))
            )
            return

        # ================
        # 例外処理:END
        # ================
        except KeyboardInterrupt:
            # キーボード割り込み
            self.stdout.write(self.style.WARNING(
                COMMON_MESSAGE_DICT["COMMAND"]["ACTION_CANCEL"].format('ユーザー作成')
            ))
            return
        except CommandError as e:
            # コマンドエラー
            raise e
        except Exception as e:
            # コマンドエラー
            raise CommandError(
                COMMON_MESSAGE_DICT["COMMAND"]["EXCECTION"].format('ユーザー作成', str(e))
            )
        
