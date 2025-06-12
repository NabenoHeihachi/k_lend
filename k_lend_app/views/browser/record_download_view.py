# =================================
# 貸出記録ダウンロードクラス
# =================================
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError, FileResponse
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE
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
# PDF関連
import io
import math
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


class RecordDownloadView(LoginRequiredMixin, TemplateView):

    # テンプレート
    template_name='k_lend_app/record_download.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "貸出記録ダウンロードクラス"
        # 共通パラメータ
        self.param = {
            "form_val_dict": {
                "record_date_from":"",
                "record_date_to":"",
            }, 
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
            FORM_NAME_LIST = ["record_date_from", "record_date_to"]
            # フォーム値辞書
            post_val_dict = {}
            record_date_from = ""
            record_date_to = ""
            # 記録一覧
            record_objects = []

            # -------------------
            # 権限チェック
            # -------------------
            # 管理者権限以外の場合
            if request.user.type_code != COMMON_ACCOUNT_TYPE_CODE["システム管理用"]:
                # 新規作成の場合
                messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["NOT_AUTHORIZED"])
                # リダイレクト
                return redirect('k_lend_app:record_list')

            # -------------------
            # フォーム値取得
            # -------------------
            for form_name in FORM_NAME_LIST:
                post_val_dict[form_name] = request.POST.get(form_name, "").strip()

            record_date_from = post_val_dict["record_date_from"] + "T00:00"
            record_date_to = post_val_dict["record_date_to"] + "T23:59"

            # -------------------
            # データバリデーション
            # -------------------
            # バリデーション結果フラグ
            is_validate_correct = True

            # *** 開始日 ***
            if not FormValidationFuncs.is_valid_datetime(record_date_from):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP_DATE_TIME"].format("開始日"))
            # *** 終了日 ***
            if not FormValidationFuncs.is_valid_datetime(record_date_to):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_INP_DATE_TIME"].format("終了日"))
            # *** 日付整合性 ***
            if is_validate_correct and not FormValidationFuncs.is_date_time_before(record_date_from, record_date_to):
                # バリデーションフラグ更新
                is_validate_correct = False
                # メッセージ表示
                messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_DATE_TIME_ORDER"].format("開始日", "終了日"))
            # *** 貸出中の貸出記録が存在しないかチェック ***
            if is_validate_correct and LoanRecordModel.objects.filter(
                    end_datetime__isnull=True,
                    ).exists():
                    # バリデーションフラグ更新
                    is_validate_correct = False
                    # メッセージ表示
                    messages.error(request, COMMON_MESSAGE_DICT["BROWSER"]["MISSING_LOAN_RECORD"])
            # -------------------
            # PDF生成
            # -------------------
            if is_validate_correct:
                # １ページデータ数
                DATA_PER_PAGE = 18
                # テーブルヘッダー
                TABLE_HEADER = ["貸出ID", "利用者", "機材", "貸出開始日時", "貸出終了日時", "備考"]
                # テーブルロー高さ
                ROW_HEIGHT = 22
                # テーブルスタイルリスト
                DEF_TABLE_STYLE_LIST = [
                        # ヘッダー行の背景をグレーに設定
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  
                        # 表で使うフォントとそのサイズを設定
                        ('FONT', (0, 0), (-1, -1), "HeiseiMin-W3", 9),
                        # 罫線を引いて、1の太さで、色は黒
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        # 四角の内側に格子状の罫線を引いて、1の太さで、色は黒
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        # 文字を上下中央
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
                        ]
                # テーブルロー高さリスト
                TABLE_HEIGHT_LIST = [ROW_HEIGHT*1.5]
                for _ in range(DATA_PER_PAGE):
                    TABLE_HEIGHT_LIST.append(ROW_HEIGHT)

                # 総合ページ数
                total_page = 1
                # 総合インデックス数
                total_index_num  = 0

                # 検索開始日と終了日をdatetimeオブジェクトに変換
                record_date_from = timezone.make_aware(datetime.strptime(record_date_from, "%Y-%m-%dT%H:%M"))
                record_date_to = timezone.make_aware(datetime.strptime(record_date_to, "%Y-%m-%dT%H:%M"))

                file_name = (
                    "records_from_" 
                    + str(post_val_dict["record_date_from"]) 
                    + "_to_" 
                    + str(post_val_dict["record_date_to"]) 
                    + "_created_at_" 
                    + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
                    + ".pdf"
                )

                # 貸出記録を取得
                record_objects = LoanRecordModel.objects.filter(
                    start_datetime__gte=record_date_from,
                    end_datetime__lte=record_date_to,
                ).order_by('-loan_id')

                # データをリストに変換
                record_list = list(record_objects)
                # データ数
                total_data = len(record_list)
                
                # ページ数を計算
                if total_data > DATA_PER_PAGE:
                    total_page = math.ceil(total_data / DATA_PER_PAGE)
                
                # メモリ上にバイナリデータを格納するオブジェクト
                buffer = io.BytesIO()

                # フォントを登録
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

                # PDFオブジェクト
                pdf_object = canvas.Canvas(buffer, pagesize=landscape(A4), bottomup=True)

                # pdfのタイトルを設定
                pdf_object.setFont('HeiseiMin-W3', 12)
                pdf_object.setTitle(
                    "機材貸出記録一覧 期間："
                    + str(post_val_dict["record_date_from"]) 
                    + "~" + str(post_val_dict["record_date_to"]) 
                    + "作成時：" + datetime.now().strftime("%Y年%m月%d日%H時%M分%S秒")
                )

                # ******** ページ作成 ********
                for _ in range(total_page):
                    # 出力データ一覧
                    output_data_list = []
                    # ヘッダーを追加
                    output_data_list.append(TABLE_HEADER)

                    # ページタイトル
                    pdf_object.setFont('HeiseiMin-W3', 12)
                    pdf_object.drawString(54, 540, "機材貸出記録一覧")

                    pdf_object.setFont('HeiseiMin-W3', 9)
                    pdf_object.drawString(54, 524, "作成日時：" + datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒"))
                    pdf_object.drawString(54, 514, "作成者：" + request.user.last_name + " " + request.user.first_name + " (" + request.user.username + ")")
                    pdf_object.drawString(54, 504, "期間：" + str(post_val_dict["record_date_from"]) + " から " + str(post_val_dict["record_date_to"]) + " まで")

                    # テーブルスタイル
                    table_style_list = DEF_TABLE_STYLE_LIST.copy()

                    # ******** ページテーブル作成 ********
                    for index_num in range(DATA_PER_PAGE):
                        row_index = index_num + 1
                        # データがある場合
                        try:
                            # ログID
                            record_id = str(record_list[total_index_num].loan_id)
                            # 利用者
                            borrower = record_list[total_index_num].borrower_name + " (" + record_list[total_index_num].borrower_id + ")"
                            # 機材
                            equipment = record_list[total_index_num].equipment.equipment_name + " (" + record_list[total_index_num].equipment.equipment_id + ")"
                            # 貸出開始日時	
                            start_datetime = localtime(record_list[total_index_num].start_datetime).strftime("%Y年%m月%d日 %H時%M分")
                            # 貸出終了日時
                            end_datetime = localtime(record_list[total_index_num].end_datetime).strftime("%Y年%m月%d日 %H時%M分")
                            # 備考
                            remarks = record_list[total_index_num].remark_text
                            
                            # 文字列長さ
                            borrower_length = len(borrower)
                            equipment_length = len(equipment)
                            remarks_length = len(remarks)

                            # ******** 利用者スタイル調節********
                            if borrower_length > 15:
                                table_style_list.append(('FONT', (1, row_index), (1, row_index), "HeiseiMin-W3", 8),)
                                borrower = borrower[:18] + "\n" + borrower[18:]
                            # ******** 機材スタイル調節********
                            if 36 >= equipment_length and equipment_length > 16:
                                table_style_list.append(('FONT', (2, row_index), (2, row_index), "HeiseiMin-W3", 8),)
                                equipment = equipment[:18] + "\n" + equipment[18:]
                            if 42 >= equipment_length and equipment_length > 36:
                                table_style_list.append(('FONT', (2, row_index), (2, row_index), "HeiseiMin-W3", 7),)
                                equipment = equipment[:21] + "\n" + equipment[21:]
                            if equipment_length > 42:
                                table_style_list.append(('FONT', (2, row_index), (2, row_index), "HeiseiMin-W3", 5),)
                                equipment = equipment[:30] + "\n" + equipment[30:60]+ "\n" + equipment[60:]
                            # ******** 備考スタイル調節********
                            if remarks_length > 15:
                                table_style_list.append(('FONT', (5, row_index), (5, row_index), "HeiseiMin-W3", 8),)
                                remarks = remarks[:16] + "\n" + remarks[16:]
                                    
                            # テーブルローデータを作成
                            row_data = [
                                record_id, 
                                borrower, 
                                equipment, 
                                start_datetime, 
                                end_datetime, 
                                remarks,
                            ]
                        # データがない場合
                        except IndexError:
                            # 空データ
                            row_data = ["", "", "", "", "", "",]

                        # テーブルローデータを追加
                        output_data_list.append(row_data)
                        # トータルインデックスをインクリメント
                        total_index_num += 1
                    
                    # テーブルオブジェクト
                    table_object = Table(
                        output_data_list, 
                        colWidths=(45, 155, 155, 115, 115, 150,), 
                        rowHeights=TABLE_HEIGHT_LIST,
                        )
                    # TableStyleを使って、Tableの装飾
                    table_object.setStyle(TableStyle(table_style_list))

                    # tableを描き出す位置を指定
                    table_object.wrapOn(pdf_object, 54, 70)
                    table_object.drawOn(pdf_object, 54, 70)

                    # ページを保存
                    pdf_object.showPage()

                # PDFファイルを保存
                pdf_object.save()

                # バッファの位置を先頭に移動
                buffer.seek(0)

                # pdf_responseを返却
                return FileResponse(buffer, as_attachment=False, filename=file_name)
            # -------------------
            # パラメータに代入
            # -------------------
            self.param["form_val_dict"] = post_val_dict

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