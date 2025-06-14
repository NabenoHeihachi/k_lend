# ====================================
# ドキュメントクラス
# ====================================
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import FileResponse, HttpResponseNotFound
import os
from k_lend_app.common.message_dict import COMMON_MESSAGE_DICT
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseServerError
# ログ
import logging
# ロガーを取得
logger = logging.getLogger(__name__)

"""
ドキュメントクラス
"""
class DocumentView(LoginRequiredMixin, TemplateView):
    CLASS_NAME = "ドキュメントクラス"

    # テンプレート
    template_name = "k_lend_app/license.html"

    def __init__(self):
        """
        コンストラクタ
        """
        # 共通パラメータ
        self.param = {
            "error" : "",
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

            document_type = ""

            if "document_type" in kwargs:
                document_type = kwargs["document_type"]
            

            if document_type == "license":
                return self.render_to_response(self.param)
            
            elif document_type == "manual":
                pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'manual.pdf')
                return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
            
            return HttpResponseNotFound(render(request, '404.html'))
        # ================
        # 例外処理:END
        # ================
        except Exception as e:
            # ログ出力
            logger.error(COMMON_MESSAGE_DICT["LOG"]["EXCEPTION_GET"].format(self.CLASS_NAME, str(e)))
            # エラーレスポンスを返す
            return HttpResponseServerError(render(request, '500.html'))
