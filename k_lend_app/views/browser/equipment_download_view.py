# =================================
# 機材確認結果ダウンロードクラス（管理用）
# =================================
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError, FileResponse
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from datetime import datetime
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
from k_lend_app.common.validation_function import FormValidationFuncs
# データベース関連
from k_lend_app.models.equipment_model import EquipmentModel
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


class EquipmentDownloadView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "機材確認結果ダウンロードクラス（管理用）"

    # テンプレート
    template_name='k_lend_app/equipment_download.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CHECK_STATUS = {
            "0": "保管中（利用可）",
            "1": "保管中（利用不可）",
            "2": "貸出中",
            "3": "故障・修理中",
            "4": "紛失中",
            "5": "その他",
        }
        self.param = {
            "equipment_objects": [],  # 機材データ一覧
            "check_status": self.CHECK_STATUS,  # 機材状態の選択肢
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
            # データ取得
            # -------------------
            # 機材一覧
            equipment_objects = EquipmentModel.objects.filter(is_active=True).order_by('equipment_id')
            # 貸出中機材一覧
            lent_equipment_ids = LoanRecordModel.objects.filter(end_datetime__isnull=True).values_list('equipment_id', flat=True)
            
            for equipment in equipment_objects:
                # 機材の貸出中フラグを設定
                equipment.is_lent = equipment.id in lent_equipment_ids

            # -------------------
            # 結果をパラメータに格納
            # -------------------
            self.param["equipment_objects"] = equipment_objects

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

            form_data_list = []

            # 機材一覧
            equipment_objects = EquipmentModel.objects.filter(is_active=True).order_by('equipment_id')

            for equipment in equipment_objects:
                # フォームデータの取得
                data_id = equipment.id
                status_key = request.POST.get(f"check_status_{data_id}", "").strip()
                remark_text = request.POST.get(f"remark_text_{data_id}", "").strip()[:32 + 1]

                # バリデーション
                if status_key not in self.CHECK_STATUS:
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["PLZ_SELECT"].format("現在の状態"))
                    return redirect('k_lend_app:equipment_download')
                
                if remark_text and not FormValidationFuncs.is_valid_text(remark_text, 1, 32):
                    messages.error(request, COMMON_MESSAGE_DICT["VALIDATION"]["INVALID_CHAR"].format("備考"))
                    return redirect('k_lend_app:equipment_download')

                # 機材情報をフォームデータに追加
                form_data_list.append({
                    "id": data_id,
                    "equipment": f"{equipment.equipment_name}（{equipment.equipment_id}）",
                    "status": self.CHECK_STATUS.get(status_key, "不明"),
                    "remark_text": remark_text,
                })
            
            # ====================
            # PDF生成
            # ====================
            # １ページデータ数
            DATA_PER_PAGE = 29
            # テーブルヘッダー
            TABLE_HEADER = ["機材","確認状態", "備考"]
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

            # ファイル名
            file_name = "equipment_check_report" +  "_created_by_" + request.user.username + "_at_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"

            # データ数
            total_data = len(form_data_list)
            
            # ページ数を計算
            if total_data > DATA_PER_PAGE:
                total_page = math.ceil(total_data / DATA_PER_PAGE)

            # メモリ上にバイナリデータを格納するオブジェクト
            buffer = io.BytesIO()

            # フォントを登録
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

            # PDFオブジェクト
            pdf_object = canvas.Canvas(buffer, pagesize=A4, bottomup=True)

            # pdfのタイトルを設定
            pdf_object.setFont('HeiseiMin-W3', 12)
            pdf_object.setTitle("機材確認結果報告書(" + request.user.username + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ")")

            # ******** ページ作成 ********
            for _ in range(total_page):
                # 出力データ一覧
                output_data_list = []
                # ヘッダーを追加
                output_data_list.append(TABLE_HEADER)

                # ページタイトル
                pdf_object.setFont('HeiseiMin-W3', 12)
                pdf_object.drawString(54, 790, "機材確認結果報告書")

                pdf_object.setFont('HeiseiMin-W3', 9)
                pdf_object.drawString(54, 775, "作成日時: " + datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                pdf_object.drawString(54, 765, "作成者ID: " + request.user.username)
                pdf_object.drawString(54, 755, "作成者名: " + request.user.last_name + " " + request.user.first_name)
                
                # テーブルスタイル
                table_style_list = DEF_TABLE_STYLE_LIST.copy()

                # ******** ページテーブル作成 ********
                for index_num in range(DATA_PER_PAGE):
                    row_index = index_num + 1
                    # データがある場合
                    try:
                        row_data = form_data_list[total_index_num]
                        equipment = row_data["equipment"]
                        status = row_data["status"]
                        remark_text = row_data["remark_text"]
                        
                        # 文字列長さ
                        equipment_len = len(equipment)
                        remark_text_len = len(remark_text)

                        # ******** 機材名調節********
                        if 42 >= equipment_len and equipment_len > 0:
                            # テーブルスタイル
                            table_style_list.append(('FONT', (0, row_index), (0, row_index), "HeiseiMin-W3", 7),)
                            equipment = equipment[:21] + "\n" + equipment[21:]
                        if 68 >= equipment_len and equipment_len > 42:
                            # テーブルスタイル
                            table_style_list.append(('FONT', (0, row_index), (0, row_index), "HeiseiMin-W3", 6),)
                            equipment = equipment[:34] + "\n" + equipment[34:]
                        if equipment_len > 68:
                            # テーブルスタイル
                            table_style_list.append(('FONT', (0, row_index), (0, row_index), "HeiseiMin-W3", 5),)
                            equipment = equipment[:40] + "\n" + equipment[40:]

                        # ******** 備考スタイル調節********
                        if remark_text_len  > 20:
                            # テーブルスタイル
                            table_style_list.append(('FONT', (2, row_index), (2, row_index), "HeiseiMin-W3", 7),)
                            remark_text = remark_text[:20] + "\n" + remark_text[20:]

                        # テーブルローデータを作成
                        row_data = [equipment, status, remark_text, ]
                    # データがない場合
                    except IndexError:
                        # 空データ
                        row_data = ["", "", "",]

                    # テーブルローデータを追加
                    output_data_list.append(row_data)
                    # トータルインデックスをインクリメント
                    total_index_num += 1
                
                # テーブルオブジェクト
                table_object = Table(
                    output_data_list, 
                    colWidths=(198, 100, 190,), 
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
    
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_POST"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))
        