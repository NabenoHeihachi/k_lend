# =================================
# バリデーション関数
# =================================
import re
from datetime import datetime

"""
フォームバリデーションクラス
"""
class FormValidationFuncs():
    def is_length_valid(input_text:str, min_length:int, max_length:int) -> bool:
        """
        入力の文字数が指定範囲内であるかをチェック
        ---
        params
            input_text 入力値
            min_length 文字数最小値
            max_length 文字数最大値
        returns
            bool 
                ture 長さ範囲内
                false 長さ範囲外
        """
        # 結果を返却
        return bool(min_length <= len(input_text) <= max_length)

    def is_convertible_to_number(input_text:str) -> bool:
        """
        入力が数字に変換可能であるかをチェック
        ---
        params
            input_text 入力値
        returns
            bool 
                ture 変換可能
                false 変換不可
        """
        # 数値に返却できる場合
        try:
            # 整数または小数に変換
            float(input_text) 
            # tureを返却
            return True
        # 数値に返却できない場合
        except ValueError:
            # falseを返却
            return False

    def has_no_special_characters(input_text:str) -> bool:
        """
        入力に特殊記号が含まれていないかをチェック
        （半角英数字と空白以外の文字を検出）
        ---
        params
            input_text 入力値
        returns
            bool 
                ture 含まれている
                false 含まれていない
        """
        # 特殊文字リスト
        special_characters = [
            "\\",  # 制御文字
            "<", ">", "&", "/", "'", '"',  # スクリプト関連文字
            "--", ";", "#", "=",  # SQLインジェクション関連文字
            "|", "¥", "*", "..", "~", "+", ":", "$"  # その他
        ]
        # 特殊文字でループ
        for special_character in special_characters:
            # 特殊文字が見つかった場合
            if special_character in input_text:
                # tureを返却
                return True
        # 特殊文字が見つからない場合
        return False

    def is_not_empty(input_text:str) -> bool:
        """
        入力が空でないかをチェック
        ---
        params
            input_text 入力値
        returns
            bool 
                ture 空値
                false 空値でない
        """
        # None 空値の場合
        if input_text != None and input_text != "":
            # tureを返却
            return True
        # None 空値でない場合
        else:
            # falseを返却
            return False
    
    def is_match(input_text: str, pattern_type: str) -> bool:
        """
        指定した正規表現に入力値がマッチしているかチェック
        
        params:
            input_text (str): チェックする文字列
            pattern_type (str): 正規表現パターンタイプ「user_id, password」
        
        returns:
            bool: マッチしている場合はTrue、そうでない場合はFalse
        """
        # 正規表現初期値
        pattern = ""

        # ユーザーIDの場合
        if pattern_type == "user_id":
            # 半角英数字大文字小文字８から３２文字
            pattern = r"^[A-Za-z0-9]{8,32}$"
        # 機材IDの場合
        elif pattern_type == "equipment_id":
            # 半角英数字大文字小文字4から３２文字
            pattern = r"^[A-Za-z0-9\-]{4,32}$"
        # パスワードの場合
        elif pattern_type == "password":
            # 半角英数字大文字小文字記号「!,?,(,),@」８から６４文字
            pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!?()@])[A-Za-z\d!?()@]{8,64}$"
        # メールアドレスの場合
        elif pattern_type == "email":
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,256}$"
        # 利用者IDの場合
        elif pattern_type == "borrower_id":
            pattern = r"^[0-9]{8}$"

        # 結果を返却
        return bool(re.fullmatch(pattern, input_text))

    def is_valid_datetime(input_datetime: str) -> bool:
        """
        入力された文字列が日時形式として有効かチェック

        Args:
            input_datetime (str): 日時文字列 (例: "2025-01-10T14:30")
        
        Returns:
            bool: 有効な日時形式であれば True、それ以外は False
        """
        try:
            # 日時形式で解析を試みる
            datetime.strptime(input_datetime, "%Y-%m-%dT%H:%M")
            return True
        except ValueError:
            return False
        
        
    def is_date_time_before(start_datetime: str, end_datetime: str) -> bool:
        """
        2つの日時文字列を比較し、start_datetimeがend_datetime よりも前かどうかチェック

        Args:
            start_datetime (str): 比較対象となる最初の時刻
            end_datetime (str): 比較対象となる2つ目の時刻

        Returns:
            bool: start_datetime が end_datetime よりも前であれば True、それ以外は False
        """

        # 時刻を datetime オブジェクトに変換
        start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M")
        end_datetime = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M")
        # 比較して結果を返す
        return bool(start_datetime <= end_datetime)
    
    def is_valid_text(input_text: str, min_length: int, max_length: int) -> bool:
        """
        入力テキストのバリデーションを行う

        Args:
            input_text (str): 入力テキスト
            min_length (int): 最小文字数
            max_length (int): 最大文字数

        Returns:
            bool: バリデーションに成功した場合は True、それ以外は False
        """
        return (
            FormValidationFuncs.is_not_empty(input_text) and
            not FormValidationFuncs.has_no_special_characters(input_text) and
            FormValidationFuncs.is_length_valid(input_text, min_length, max_length)
        )
    