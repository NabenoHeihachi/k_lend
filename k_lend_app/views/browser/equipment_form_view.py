# =================================
# 機材フォームクラス（管理用）
# =================================
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
from k_lend_app.common.validation_function import FormValidationFuncs
# データベース関連
from k_lend_app.models.equipment_model import EquipmentModel
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


class EquipmentFormView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "機材フォームクラス（管理用）"

    # テンプレート
    template_name='k_lend_app/equipment_form.html'

    def __init__(self):
        """
        コンストラクタ
        """
        # 共通パラメータ
        self.param = {
            "form_val_dict" : {},
            "is_edit" : False
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

            # 初期値
            model_id = None
            equipment_object = None

            # -------------------
            # 情報取得
            # -------------------
            # URLにIDがある場合
            if "model_id" in kwargs:
                # IDを取得
                model_id = kwargs["model_id"]
                try:
                    # データを取得
                    equipment_object = get_object_or_404(EquipmentModel, pk=model_id)
                except:
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["RECORD_NOT_FOUND"].format("指定の機材情報"))
                    return redirect('k_lend_app:equipment_list')

            # -------------------
            # パラメータに代入
            # -------------------
            if model_id and equipment_object:
                self.param["form_val_dict"]["equipment_id"] = equipment_object.equipment_id
                self.param["form_val_dict"]["equipment_name"] = equipment_object.equipment_name
                self.param["form_val_dict"]["remark_text"] = equipment_object.remark_text
                self.param["is_edit"] = True

            # レンダリング
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

            # 全フォーム名リスト
            FORM_NAME_LIST = ["equipment_id", "equipment_name", "remark_text"]

            # 更新ID
            model_id = None
            # バリデーション結果フラグ
            is_validate_correct = True
            # POSTデータ値辞書初期値
            post_val_dict = {}
            
            # -------------------
            # POSTタイプ識別
            # -------------------
            # URLにIDがある場合
            if "model_id" in kwargs:
                # IDを取得
                model_id = kwargs["model_id"]

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
            VALIDATION_MSG = COMMON_MESSAGE_DICT["VALIDATION"]
            # ***機材ID***
            if not FormValidationFuncs.is_match(post_val_dict["equipment_id"], "equipment_id"):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["RE_EQUIPMENT_ID"])

            # ***機材名***
            # 空値の場合
            if not FormValidationFuncs.is_not_empty(post_val_dict["equipment_name"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("機材名", 3, 48))
            # 長さに不正がある場合
            elif not FormValidationFuncs.is_length_valid(post_val_dict["equipment_name"], 3, 48):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("機材名", 3, 48))
            # 特殊文字が含まれている場合
            elif FormValidationFuncs.has_no_special_characters(post_val_dict["equipment_name"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["INVALID_CHAR"].format("機材名"))

            # ***備考***
            # 長さが不適切な場合
            if post_val_dict["remark_text"] and not FormValidationFuncs.is_length_valid(post_val_dict["remark_text"], 1, 256):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("備考", 1, 256))
            # 特殊文字が含まれている場合
            elif FormValidationFuncs.has_no_special_characters(post_val_dict["remark_text"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示                
                messages.error(request, VALIDATION_MSG["INVALID_CHAR"].format("備考"))
            
            # -------------------
            # DB登録
            # -------------------
            # バリデーションエラーがない場合
            if is_validate_correct:
                try:
                    # <<<<< モデル取得 >>>>>>
                    equipment_model = EquipmentModel()
                    if model_id:
                        equipment_model = get_object_or_404(EquipmentModel, pk=model_id)
                        

                    # *** 作成 ***
                    equipment_model.equipment_id = post_val_dict["equipment_id"]
                    equipment_model.equipment_name = post_val_dict["equipment_name"]
                    # 備考
                    if post_val_dict["remark_text"]:
                        equipment_model.remark_text = post_val_dict["remark_text"]
                    else:
                        equipment_model.remark_text = ""
                    # 更新
                    equipment_model.updated_by = request.user
                    if model_id:
                        # 作成者
                        equipment_model.created_by = request.user

                    #  *** 変更の保存 ***
                    equipment_model.save()

                    messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format("機材情報"))
                    # リダイレクト
                    if model_id:
                        # 新規登録の場合
                        return redirect('k_lend_app:equipment_edit', model_id=model_id)
                    return redirect('k_lend_app:equipment_list')
                # ユーニーク制約違反の場合
                except IntegrityError:
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["ALREADY_REGISTERED"].format("機材ID"))
                    
                except Exception as e:
                    logger.error(COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("機材情報") + str(e))
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("機材情報"))
                
            # -------------------
            # パラメータに代入
            # -------------------
            self.param["form_val_dict"] = post_val_dict
            if model_id:
                self.param["is_edit"] = True
            
            # エラー時の再描画
            return self.render_to_response(self.param)
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))