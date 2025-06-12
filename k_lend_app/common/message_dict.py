# =================================
# メッセージ辞書
# =================================
from k_lend_app.common.account_type_code import COMMON_ACCOUNT_TYPE_CODE

# メッセージ辞書
COMMON_MESSAGE_DICT = {
    # <<<< バリデーション >>>>>
    "VALIDATION": {
        # ERROR
        "PLZ_INP": "{0}を{1}文字以上{2}文字以内で入力してください。",
        "PLZ_SELECT": "{0}を選択してください。",
        "PLZ_INP_DATE_TIME": "{0}を日付時刻形式で入力してください。",
        "PLZ_INP_EMAIL": "{0}を有効なメールアドレス形式で入力してください。",
        "PLZ_INP_NUMERIC": "{0}を数値形式で入力してください。",
        "INVALID_INPUT": "入力された{0}はご利用できません。",
        "INVALID_CHAR": "{0}に使用できない記号や特殊文字が含まれています。",
        "INVALID_DATE_TIME_ORDER": "{0}が{1}以前の日付時刻となるように入力してください。",
        "INVALID_ID": "{0}IDが不正です。再度ページを読み直してからお試しください。",
        "INVALID_ONE_TIME_PASSWORD": "ワンタイムパスワードが一致しません。もう一度お試しください。",
        "ACCOUNT_UNUSABLE": "このアカウントは、{0}ご利用できません。",
        "RE_EQUIPMENT_ID": "機材IDは、半角の英大文字・小文字・数字から構成し、4文字以上64文字以内で入力してください。",
        "RE_USER_ID": "ユーザーIDは、半角の英大文字・小文字・数字から構成し、8文字以上32文字以内で入力してください。",
        "RE_BORROWER_ID": "利用者IDは、半角の数字から構成し、8文字で入力してください。",
        "RE_PASSWORD": "パスワードは、半角の英大文字・小文字・数字・記号「!,?,(,)」を含み、８文字以上６４文字以内で入力してください。",
        "PASSWORD_CONFIRM": "パスワードが一致しません。",
        "AUTH_FAILED": "ユーザー名またはパスワードが正しくありません。",
        "NOT_AUTHORIZED": "{0}の権限がありません。",
    },

    # <<<<< DB >>>>>
    "DB": {
        # INFO
        "RECORD_NOT_FOUND": "{0}は見つかりませんでした。",
        # SUCCESS
        "SAVE_SUCCESS": "{0}が正常に保存されました。",
        "DELETE_SUCCESS": "{0}が正常に削除されました。",
        "UPDATE_SUCCESS": "{0}が正常に更新されました。",
        "CREATE_SUCCESS": "{0}が正常に作成されました。",
        # ERROR
        "ALREADY_REGISTERED": "{0}はすでに登録されています。",
        "SAVE_ERROR": "{0}保存中に予期しないエラーが発生しました。",
        "DELETE_ERROR": "{0}削除中に予期しないエラーが発生しました。",
        "UPDATE_ERROR": "{0}更新中に予期しないエラーが発生しました。",
        "CREATE_ERROR": "{0}作成中に予期しないエラーが発生しました。",
    },

    # <<<<< コマンド >>>>>
    "COMMAND": {
        # INFO
        "PLZ_INP": "{0}を入力してください: ",
        "PLZ_INP_HID": "{0}を入力してください: （非表示）",
        "CFM_CREATE": "\n{0}作成しますか？（y/n）:",
        "ACCOUNT_TYPE_CHOICES":"\n（" + ", ".join(f"{k}={v}" for k, v in COMMON_ACCOUNT_TYPE_CODE.items()) + "）",
        # SUCCESS
        "ACTION_SUCCESS": "\n\n{0}処理が正常に完了しました。",
        # ERROR
        "EXCECTION": "\n{0}処理中に予期しないエラーが発生しました: {1}",
        # WARNING
        "ACTION_CANCEL": "\n{0}処理はキャンセルされました。",
    },

    # <<<< ブラウザ >>>>
    "BROWSER": {
        # INFO
        # SUCCESS
        "ACTION_SUCCESS": "{0}処理が正常に完了しました。",
        # ERROR
        "PLZ_ACTION": "{0}してください。",
        "ACTION_ERROR": "{0}処理に失敗しました。再度お試しください。",
        "NOT_AUTHORIZED": "必要な権限がありません。",
        "INVALID_REQUEST": "無効なリクエストです。再度お試しください。",
        # WARNING
        "MISSING_LOAN_RECORD": "指定期間内に貸出中のデータがあります。",
    },

    # <<<<< ログ >>>>>
    "LOG": {
        # INFO
        "VIEW_GET": "-----【{0} 処理:GET】-----",
        "VIEW_POST": "-----【{0} 処理:POST】-----",
        "VIEW_SSE": "-----【{0} 処理:SSE】-----",
        # SUCCESS
        # ERROR
        "EXCEPTION_GET": "EXCEPTION ERROR【{0} 処理:GET 】: {1}",
        "EXCEPTION_POST": "EXCEPTION ERROR【{0} 処理:POST 】: {1}",
        "EXCEPTION_SSE": "EXCEPTION ERROR【{0} 処理:SSE 】: {1}",
        # WARNING
    },
}