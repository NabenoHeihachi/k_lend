# =================================
# アクセス制限系関数
# =================================
from django.core.exceptions import PermissionDenied
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE

def restrict_page_access_by_type_code(request, need_permission):
    """
    不正アクセス時404エラー
    概要: ユーザーのtype_codeに基づいて不正アクセス時403エラー発生させる
    ---
    params
        request: HttpRequest
        need_permission: str
            システム管理：システム管理職員用アカウントのみ
            職員：システム管理と貸出情報管理用の職員アカウントのみ
    returns
        なし
    """    
    # ユーザータイプコードが適切かチェック
    is_correct = False
    # ユーザータイプコード
    type_code = request.user.type_code

    # <<<<< システム管理の場合 >>>>>
    if need_permission == "システム管理":
        if type_code == COMMON_ACCOUNT_TYPE_CODE["システム管理用"]:
            is_correct = True

    # <<<<< 職員の場合 >>>>>
    elif need_permission == "職員":
        if(type_code == COMMON_ACCOUNT_TYPE_CODE["貸出情報管理用"] or
            type_code == COMMON_ACCOUNT_TYPE_CODE["システム管理用"]):
            is_correct = True
    
    # 権限がない場合
    if is_correct == False:
        # 403エラーを発生
        # エラーレスポンスを返す
        raise PermissionDenied("権限がありません。")