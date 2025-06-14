# =================================
# 貸出記録フォームクラス
# =================================
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import localtime
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
from k_lend_app.common.validation_function import FormValidationFuncs
# データベース関連
from k_lend_app.models.loan_record_model import LoanRecordModel
from k_lend_app.models.equipment_model import EquipmentModel
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


class RecordFormView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "貸出記録フォームクラス"

    # テンプレート
    template_name='k_lend_app/record_form.html'

    def __init__(self):
        """
        コンストラクタ
        """
        # 共通パラメータ
        self.param = {
            "form_val_dict" : {},
            "equipment_list" : None,
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
            loan_id = None
            record_object = None

            # -------------------
            # 機材ID取得
            # -------------------
            # GETパラメータから機材IDを取得
            url_equipment_id = request.GET.get("equipment", "").strip()

            # 機材IDがある場合、整数値に変換
            if url_equipment_id:
                try:
                    int(url_equipment_id)
                except:
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_ID"].format("機材"))
                    return redirect('k_lend_app:record_create')
            
            # -------------------
            # 情報取得
            # -------------------
            # URLにIDがある場合
            if "loan_id" in kwargs:
                # IDを取得
                loan_id = kwargs["loan_id"]
                try:
                    # データを取得
                    record_object = get_object_or_404(LoanRecordModel, pk=loan_id)
                except:
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["RECORD_NOT_FOUND"].format("指定の貸出記録"))
                    return redirect('k_lend_app:record_list')

            # -------------------
            # パラメータに代入
            # -------------------
            if url_equipment_id:
                self.param["form_val_dict"]["equipment_model_id"] = str(url_equipment_id)
            

            if loan_id and record_object:
                self.param["form_val_dict"]["borrower_id"] = record_object.borrower_id
                self.param["form_val_dict"]["borrower_name"] = record_object.borrower_name
                self.param["form_val_dict"]["equipment_model_id"] = record_object.equipment.id
                self.param["form_val_dict"]["start_datetime"] = localtime(record_object.start_datetime).strftime('%Y-%m-%dT%H:%M')
                if record_object.end_datetime:
                    self.param["form_val_dict"]["end_datetime"] = localtime(record_object.end_datetime).strftime('%Y-%m-%dT%H:%M')
                else:
                    self.param["form_val_dict"]["end_datetime"] = ""

                self.param["form_val_dict"]["remark_text"] = record_object.remark_text
                self.param["is_edit"] = True
            
                # 機材リストを取得
                self.param["equipment_list"] = EquipmentModel.objects.all().order_by('equipment_name')
            else:
                # 機材リストを取得
                self.param["equipment_list"] = EquipmentModel.objects.filter(is_active=True).order_by('equipment_name')
            
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
            FORM_NAME_LIST = [
                "borrower_id", 
                "borrower_name", 
                "equipment_model_id", 
                "start_datetime", 
                "end_datetime", 
                "remark_text"
            ]

            # 更新ID
            loan_id = None
            # バリデーション結果フラグ
            is_validate_correct = True
            # POSTデータ値辞書初期値
            post_val_dict = {}
            # 機材オブジェクト
            equipment_object = None
            
            # -------------------
            # POSTタイプ識別
            # -------------------
            # URLにIDがある場合
            if "loan_id" in kwargs:
                # IDを取得
                loan_id = kwargs["loan_id"]

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
            # ***利用者ID***
            if not FormValidationFuncs.is_match(post_val_dict["borrower_id"], "borrower_id"):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["RE_BORROWER_ID"])

            # ***利用者名***
            # 空値の場合
            if not FormValidationFuncs.is_not_empty(post_val_dict["borrower_name"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("利用者名", 3, 32))
            # 長さに不正がある場合
            elif not FormValidationFuncs.is_length_valid(post_val_dict["borrower_name"], 3, 32):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("利用者名", 3, 32))
            # 特殊文字が含まれている場合
            elif FormValidationFuncs.has_no_special_characters(post_val_dict["borrower_name"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["INVALID_CHAR"].format("利用者名"))
            
            # ***機材ID***
            try:
                int(post_val_dict["equipment_model_id"])
                # 機材オブジェクト取得
                equipment_object = get_object_or_404(EquipmentModel, pk=post_val_dict["equipment_model_id"])
            except Exception as e:
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_SELECT"].format("機材"))
            
            # ***開始日時***
            if not FormValidationFuncs.is_valid_datetime(post_val_dict["start_datetime"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP_DATE_TIME"].format("開始日時"))
            
            # ***終了日時***
            if post_val_dict["end_datetime"] and not FormValidationFuncs.is_valid_datetime(post_val_dict["end_datetime"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP_DATE_TIME"].format("終了日時"))
            
            # 開始日時と終了日時の順序チェック
            if is_validate_correct and post_val_dict["end_datetime"] and not FormValidationFuncs.is_date_time_before(post_val_dict["start_datetime"], post_val_dict["end_datetime"]):
                    # バリデーションフラグ更新
                    is_validate_correct = False
                    # メッセージ表示
                    messages.error(request, VALIDATION_MSG["INVALID_DATE_TIME_ORDER"].format("開始日時", "終了日時"))

            # ***備考***
            # 長さが不適切な場合
            if post_val_dict["remark_text"] and not FormValidationFuncs.is_length_valid(post_val_dict["remark_text"], 1, 32):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, VALIDATION_MSG["PLZ_INP"].format("備考", 1, 32))
            # 特殊文字が含まれている場合
            elif FormValidationFuncs.has_no_special_characters(post_val_dict["remark_text"]):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示                
                messages.error(request, VALIDATION_MSG["INVALID_CHAR"].format("備考"))
            
            # -------------------
            # 時刻変換
            # -------------------
            if is_validate_correct:
                # *** 開始日時の変換 ***
                start_datetime = post_val_dict["start_datetime"]
                start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M")
                start_datetime = timezone.make_aware(start_datetime)
                post_val_dict["start_datetime"] = start_datetime
                # *** 終了日時の変換 ***
                if post_val_dict["end_datetime"]:
                    end_datetime = post_val_dict["end_datetime"]
                    end_datetime = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M")
                    end_datetime = timezone.make_aware(end_datetime)
                    post_val_dict["end_datetime"] = end_datetime


            # -------------------
            # DB登録
            # -------------------
            # バリデーションエラーがない場合
            if is_validate_correct:
                try:
                    # <<<<< モデル取得 >>>>>>
                    record_model = LoanRecordModel()
                    if loan_id:
                        record_model = get_object_or_404(LoanRecordModel, pk=loan_id)
                        

                    # *** 作成 ***
                    record_model.borrower_id = post_val_dict["borrower_id"]
                    record_model.borrower_name = post_val_dict["borrower_name"]
                    record_model.equipment = equipment_object
                    record_model.start_datetime = post_val_dict["start_datetime"]
                    if post_val_dict["end_datetime"]:
                        record_model.end_datetime = post_val_dict["end_datetime"]
                    else:
                        record_model.end_datetime = None
                    # 備考
                    if post_val_dict["remark_text"]:
                        record_model.remark_text = post_val_dict["remark_text"]
                    else:
                        record_model.remark_text = ""
                    # 更新者
                    record_model.updated_by = request.user
                    # *** 更新 ***
                    if not loan_id:
                        # 作成者
                        record_model.created_by = request.user

                    #  *** 変更の保存 ***
                    record_model.save()

                    messages.success(request, COMMON_MESSAGE_DICT["DB"]["SAVE_SUCCESS"].format("貸出情報"))
                    # リダイレクト
                    if loan_id:
                        # 新規登録の場合
                        return redirect('k_lend_app:record_edit', loan_id=loan_id)
                    return redirect('k_lend_app:record_list')
                # ユーニーク制約違反の場合
                except IntegrityError:
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["ALREADY_REGISTERED"].format("貸出ID"))
                    
                except Exception as e:
                    logger.error(COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("貸出情報") + str(e))
                    messages.error(request, COMMON_MESSAGE_DICT["DB"]["SAVE_ERROR"].format("貸出情報"))
                
            # -------------------
            # パラメータに代入
            # -------------------
            # POST値をパラメータに代入
            self.param["form_val_dict"] = post_val_dict
            # 機材リストを取得
            self.param["equipment_list"] = EquipmentModel.objects.filter(is_active=True).order_by('equipment_name')
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