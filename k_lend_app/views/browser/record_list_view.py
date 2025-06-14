# =================================
# 貸出記録一覧クラス
# =================================
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.http import HttpResponseServerError
from django.core.paginator import Paginator
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
# SQL関連
from django.db.models import Q
# データベース関連
from k_lend_app.models.loan_record_model import LoanRecordModel
from k_lend_app.models.equipment_model import EquipmentModel
# フォームバリデーションクラス
from k_lend_app.common.validation_function import FormValidationFuncs
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)

class RecordListView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "貸出記録一覧クラス"

    # テンプレートファイル
    template_name='k_lend_app/record_list.html'

    def __init__(self):
        """
        コンストラクタ
        """
        # 共通パラメータ
        self.param = {
            "record_objects": [], 
            "search_val_dict":{},
            "equipment_list" : None,
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
                "is_return":"",
                "equipment_model_id": "",
            }

            # セッションに検索データがある場合
            if 'record_list_search_val_dict' in request.session:
                # セッションからデータを取得
                session_search_val_dict = self.request.session["record_list_search_val_dict"]
                
                # 検索条件を代入
                search_val_dict["name_or_id"] = session_search_val_dict["name_or_id"]
                search_val_dict["is_return"] = session_search_val_dict["is_return"]
                search_val_dict["equipment_model_id"] = session_search_val_dict["equipment_model_id"]
            # -------------------
            # データ取得
            # -------------------
            # データ取得
            record_objects = LoanRecordModel.objects.all().order_by("-loan_id")

            # 検索条件を適用（AND検索）
            # *** 氏名・学籍番号 ***
            if search_val_dict["name_or_id"]:
                record_objects = record_objects.filter(
                    Q(borrower_id__icontains=search_val_dict["name_or_id"]) |
                    Q(borrower_name__icontains=search_val_dict["name_or_id"])
                )

            # *** 貸出フラグ ***
            if search_val_dict["is_return"] == "0":
                record_objects = record_objects.filter(end_datetime__isnull=False)
            elif search_val_dict["is_return"] == "1":
                record_objects = record_objects.filter(end_datetime__isnull=True)
            
            # *** 機器ID ***
            if search_val_dict["equipment_model_id"]:
                record_objects = record_objects.filter(equipment__id=search_val_dict["equipment_model_id"])

            record_objects = record_objects.order_by("-loan_id")

            paginated_record_objects = Paginator(record_objects, 8)

            page_number = request.GET.get('page', '1')
            page_obj = paginated_record_objects.get_page(page_number)
            
            # -------------------
            # 結果をパラメータに格納
            # -------------------
            self.param["equipment_list"] = EquipmentModel.objects.all().order_by('-is_active', 'equipment_name')
            self.param["record_objects"] = page_obj
            self.param["search_val_dict"] = search_val_dict
            self.param["page_obj"] = page_obj

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
            # 削除処理場合
            # ================
            if button_action == "delete":
                loan_id = request.POST.get('loan_id', '')
                # バリデーション結果フラグ
                is_validate_correct = True

                # バリデーション処理
                if not FormValidationFuncs.is_not_empty(loan_id):
                    is_validate_correct = False
                # バリデーション処理
                elif not FormValidationFuncs.is_convertible_to_number(loan_id):
                    is_validate_correct = False
                    
                # <<<<< エラーがない場合 >>>>>
                if is_validate_correct:
                    try:
                        # 削除処理
                        record_object = get_object_or_404(LoanRecordModel, pk=loan_id)
                        record_object.delete()
                        
                        # メッセージ
                        messages.success(request, COMMON_MESSAGE_DICT["DB"]["DELETE_SUCCESS"].format(f"貸出記録（ID:{loan_id}）"))
                        # リダイレクト
                        return redirect('k_lend_app:record_list')
                    except Exception as e:
                        logger.error(COMMON_MESSAGE_DICT["DB"]["DELETE_ERROR"].format(f"貸出記録（ID:{loan_id}）" + str(e)))
                
            # ================
            # 検索処理場合
            # ================
            elif  button_action == "search":
                # 検索条件初期値
                search_val_dict = {
                    "name_or_id":"",
                    "is_return":"",
                    "equipment_model_id": "",
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
                    if not FormValidationFuncs.is_length_valid(search_val_dict["name_or_id"], 1, 32):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP"].format("検索文字列", 1, 32))
                    elif FormValidationFuncs.has_no_special_characters(search_val_dict["name_or_id"]):
                        is_validate_correct = False
                        messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format("検索文字列"))
                
                if search_val_dict["is_return"] not in ["0", "1", ""]:
                    is_validate_correct = False
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_SELECT"].format("貸出状態"))
                
                if search_val_dict["equipment_model_id"] and not FormValidationFuncs.is_convertible_to_number(search_val_dict["equipment_model_id"]):
                    is_validate_correct = False
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_SELECT"].format("機材"))

                
                # -------------------
                # 検索条件保存
                # -------------------
                if is_validate_correct:
                    # セッションに代入
                    self.request.session["record_list_search_val_dict"] = search_val_dict

                # リダイレクト
                return redirect('k_lend_app:record_list')

            # ==============================
            # ボタンアクションに該当がない場合
            # ==============================
            messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["INVALID_REQUEST"])
            return redirect('k_lend_app:record_list')
        
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))