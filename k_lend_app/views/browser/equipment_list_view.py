# =================================
# 機材一覧クラス（管理用）
# =================================
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
from k_lend_app.common.validation_function import FormValidationFuncs
# データベース関連
from django.db.models import Q
from k_lend_app.models.equipment_model import EquipmentModel
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


class EquipmentListView(LoginRequiredMixin, TemplateView):

    # テンプレート
    template_name='k_lend_app/equipment_list.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "機材一覧クラス（管理用）"
        # 共通パラメータ
        self.param = {
            "equipment_objects": [],  # 機材データ一覧
            "search_val_dict":{},
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

            # -------------------
            # 検索条件取得
            # -------------------
            # 検索条件初期値
            search_val_dict = {
                "name_or_id":"",
            }

            # セッションに検索データがある場合
            if 'equipment_list_search_val_dict' in request.session:
                # セッションからデータを取得
                session_search_val_dict = self.request.session["equipment_list_search_val_dict"]
                
                # 検索条件を代入
                search_val_dict["name_or_id"] = session_search_val_dict["name_or_id"]
            # -------------------
            # データ取得
            # -------------------
            # データ取得
            equipment_objects = EquipmentModel.objects.all().order_by('-is_active', 'equipment_id')

            # 検索条件を適用（AND検索）
            # 氏名・学籍番号
            if search_val_dict["name_or_id"]:
                equipment_objects = equipment_objects.filter(
                    Q(equipment_id__icontains=search_val_dict["name_or_id"]) |
                    Q(equipment_name__icontains=search_val_dict["name_or_id"])
                )
            # -------------------
            # 結果をパラメータに格納
            # -------------------
            self.param["equipment_objects"] = equipment_objects
            self.param["search_val_dict"] = search_val_dict

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

            # ================
            # 有効処理場合
            # ================
            if button_action == "change_active":
                model_id = request.POST.get('model_id', '')
                # バリデーション結果フラグ
                is_validate_correct = True

                # バリデーション処理
                if not FormValidationFuncs.is_not_empty(model_id):
                    is_validate_correct = False
                # バリデーション処理
                elif not FormValidationFuncs.is_convertible_to_number(model_id):
                    is_validate_correct = False
                    
                # <<<<< エラーがない場合 >>>>>
                if is_validate_correct:
                    try:
                        # 削除処理
                        equipment_object = get_object_or_404(EquipmentModel, pk=model_id)
                        equipment_object.is_active = not equipment_object.is_active
                        equipment_object.save()
                        # メッセージ
                        messages.success(request, COMMON_MESSAGE_DICT["DB"]["UPDATE_SUCCESS"].format(f"機材（{equipment_object.equipment_id}）の有効/無効"))
                        # リダイレクト
                        return redirect('k_lend_app:equipment_list')
                    except Exception as e:
                        logger.error(COMMON_MESSAGE_DICT["DB"]["UPDATE_ERROR"].format(f"機材（ID:{model_id}）の有効/無効" + str(e)))
                
            # ================
            # 検索処理場合
            # ================
            elif  button_action == "search":
                # 検索条件初期値
                search_val_dict = {
                    "name_or_id":"",
                }

                # 検索パラメータ取得
                for form_name in search_val_dict:
                    search_val_dict[form_name] = request.POST.get(form_name, '').strip()[:128]

                # -------------------
                # データバリデーション
                # -------------------
                # バリデーション結果フラグ
                is_validate_correct = True

                # バリデーション
                if search_val_dict["name_or_id"]:
                    if not FormValidationFuncs.is_length_valid(search_val_dict["name_or_id"], 1, 64):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format("検索文字列", 1, 64))
                    elif FormValidationFuncs.has_no_special_characters(search_val_dict["name_or_id"]):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format("検索文字列"))
                
                # -------------------
                # 検索条件保存
                # -------------------
                if is_validate_correct:
                    # セッションに代入
                    self.request.session["equipment_list_search_val_dict"] = search_val_dict

                # リダイレクト
                return redirect('k_lend_app:equipment_list')

            # ==============================
            # ボタンアクションに該当がない場合
            # ==============================
            messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["INVALID_REQUEST"])
            return redirect('k_lend_app:equipment_list')
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))