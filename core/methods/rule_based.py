import os
import openpyxl
from typing import List, Dict
from core.methods.base import BaseProofreader

class RuleBasedProofreader(BaseProofreader):
    """
    Excelファイルから定義されたルールを読み込み、添削を行うクラス
    """
    def __init__(self, excel_path: str = "rules.xlsx"):
        super().__init__()
        self.excel_path = excel_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, str]]:
        """
        Excelからルールを読み込みます。
        期待するフォーマット: 1行目はヘッダー [検索単語, 修正後, 理由]
        """
        rules = []
        if not os.path.exists(self.excel_path):
            print(f"警告: ルールファイル {self.excel_path} が見つかりません。")
            return rules

        try:
            wb = openpyxl.load_workbook(self.excel_path, data_only=True)
            ws = wb.active
            
            # 2行目から読み込み (1行目はヘッダー想定)
            for row in ws.iter_rows(min_row=2, values_only=True):
                original = row[0]
                corrected = row[1]
                reason = row[2]
                
                if original: # 検索単語がある場合のみ追加
                    rules.append({
                        "original": str(original),
                        "corrected": str(corrected) if corrected else "",
                        "reason": str(reason) if reason else ""
                    })
            wb.close()
        except Exception as e:
            print(f"ルール読み込み中にエラーが発生しました: {e}")
            
        return rules

    def proofread(self, text: str) -> List[Dict[str, str]]:
        actual_corrections = []
        for rule in self.rules:
            if rule["original"] in text:
                actual_corrections.append(rule)
        return actual_corrections
