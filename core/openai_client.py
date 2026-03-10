import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("APIキーが設定されていません。")
        self.client = OpenAI(api_key=self.api_key)

    def proofread(self, text: str) -> List[Dict[str, str]]:
        """
        【テストモード】テキストを解析せず、ダミーの修正箇所を返します。
        """
        print("--- テストモード (Mock) で実行中 ---")
        
        # テスト用のダミーデータ（入力テキストに特定の単語が含まれている場合に反応させる）
        dummy_corrections = [
            {
                "original": "、",
                "corrected": "、",
                "reason": "句読点の後は一文字空ける習慣があるかもしれませんが、ここでは文脈を確認してください（テスト表示）。"
            },
            {
                "original": "です",
                "corrected": "である",
                "reason": "文末を常体に統一することを検討してください（テスト表示）。"
            },
            {
                "original": "ます",
                "corrected": "る",
                "reason": "語尾のバリエーションを増やすと読みやすくなります（テスト表示）。"
            }
        ]
        
        # 入力テキストに含まれる単語だけを抽出して返す（シミュレーション）
        actual_corrections = []
        for d in dummy_corrections:
            if d["original"] in text:
                actual_corrections.append(d)
        
        return actual_corrections
