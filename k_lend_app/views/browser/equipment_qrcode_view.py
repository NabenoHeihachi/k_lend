# =================================
# 機材QRコード表示クラス（管理用）
# =================================
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.urls import reverse
from urllib.parse import urlencode
# セキュリティ関連
from k_lend_app.common.access_function import restrict_page_access_by_type_code
from django.contrib.auth.mixins import LoginRequiredMixin
# データベース関連
from k_lend_app.models.equipment_model import EquipmentModel
# QRコード生成関連
import qrcode
import base64
from io import BytesIO
# ログ
import logging

# ロガーを取得
logger = logging.getLogger(__name__)


class EquipmentQRCodeView(LoginRequiredMixin, TemplateView):

    # テンプレート
    template_name='k_lend_app/equipment_qrcode.html'

    def __init__(self):
        """
        コンストラクタ
        """
        self.CLASS_NAME = "機材QRコード表示クラス（管理用）"
        # 共通パラメータ
        self.param = {
            "management_qrcode_base64_str": None,  # 管理用QRコード画像
            "recordkeeping_qrcode_base64_str": None,  # 記録用QRコード画像
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

            equipment_object = None  # 機材オブジェクト初期化
            # QRコード初期値
            recordkeeping_qrcode_base64_str = None
            management_qrcode_base64_str = None

            # -------------------
            # 情報取得
            # -------------------
            # URLにIDがある場合
            model_id = kwargs["model_id"]
            try:
                # データを取得
                equipment_object = get_object_or_404(EquipmentModel, pk=model_id)
            except:
                messages.error(request, COMMON_MESSAGE_DICT["DB"]["RECORD_NOT_FOUND"].format("指定の機材情報"))
                return redirect('k_lend_app:equipment_list')
            
            # --------------------
            # QRコード生成
            # --------------------
            # URLを取得
            equipment_edit_url = reverse('k_lend_app:equipment_edit', kwargs={'model_id': model_id})
            equipment_recordkeeping_url = reverse('k_lend_app:record_create') + '?' + urlencode({'equipment': model_id})

            # 管理用QRコードのBase64エンコード文字列を取得
            management_qrcode_base64_str = self.get_qrcode_base64_str(request.build_absolute_uri(equipment_edit_url))
            # 記録用QRコードのBase64エンコード文字列を取得
            recordkeeping_qrcode_base64_str = self.get_qrcode_base64_str(request.build_absolute_uri(equipment_recordkeeping_url))

            # -------------------
            # パラメータに代入
            # -------------------
            # 機材オブジェクト
            self.param["equipment_object"] = equipment_object
            # 管理用QRコード画像をBase64エンコード
            self.param["management_qrcode_base64_str"] = management_qrcode_base64_str
            # 記録用QRコード画像をBase64エンコード
            self.param["recordkeeping_qrcode_base64_str"] = recordkeeping_qrcode_base64_str

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
        
    
    def get_qrcode_base64_str(self, url):
        """
        指定されたURLのQRコードを生成し、Base64エンコードされた文字列を返す
        """
        # QRコードを生成
        qr_code_image_obj = qrcode.make(url)
        
        # PNG画像としてメモリに保存するためのバッファを用意
        memory_image_buffer = BytesIO()
        qr_code_image_obj.save(memory_image_buffer, format="PNG")
        
        # メモリ上のPNG画像をbase64にエンコード（HTMLで埋め込めるように）
        png_binary_data = memory_image_buffer.getvalue()
        png_base64_bytes = base64.b64encode(png_binary_data)
        png_base64_str = png_base64_bytes.decode("utf-8")
        
        return png_base64_str