import json
import requests
import re
from typing import List, Dict
from core.methods.base import BaseProofreader
from core.config import config_manager

class CustomAIProofreader(BaseProofreader):
    """
    社内AIサーバー等の独自エンドポイントを直接呼び出して添削を行うクラス。
    方法4（マルチエージェント方式）に基づき、構成レビュー、用語統一、詳細校正の3パスで実行します。
    """
    def __init__(self):
        super().__init__()
        self.endpoint_url = config_manager.get("custom_ai_url", "")
        self.api_key = config_manager.get("custom_ai_api_key", "")
        self.model = config_manager.get("openai_model", "gpt-4o-mini")
        self.system_prompt = config_manager.get("system_prompt", "")
        self.max_tokens = 2048  # 複数パスの統合結果を考慮し少し拡大
        
        # チャンク設定（詳細校正用）
        self.max_chunk_chars = 2000 
        
        if not self.endpoint_url:
            raise ValueError("AIエンドポイントURLが設定されていません。設定画面から登録してください。")

    def proofread(self, text: str) -> List[Dict[str, str]]:
        """
        3つのパスを順番に実行し、すべての添削結果を統合して返します。
        """
        if not text or not text.strip():
            return []

        all_corrections = []

        # パス1: 全体構成・論理レビュー（全文一括）
        print("--- パス1: 全体構成・論理レビューを実行中 ---")
        review_corrections = self._run_review_pass(text)
        all_corrections.extend(review_corrections)

        # パス2: 用語統一・表記揺れチェック（全文一括）
        print("--- パス2: 用語統一・表記揺れチェックを実行中 ---")
        term_corrections = self._run_terminology_pass(text)
        all_corrections.extend(term_corrections)

        # パス3: 詳細校正（チャンク分割）
        # ステップ2で見つかった用語ルールを考慮に入れる（改善の余地あり）
        print("--- パス3: 詳細校正を実行中 ---")
        detail_corrections = self._run_detail_pass(text)
        all_corrections.extend(detail_corrections)

        return all_corrections

    def _run_review_pass(self, text: str) -> List[Dict[str, str]]:
        """構成や論理の飛躍をチェックするパス。"""
        system_content = """あなたはプロの技術ドキュメントレビュアーです。
文章全体を俯瞰し、以下の観点で「修正が必要な大きな問題」を指摘してください。

1. 技術報告書としての構成（背景・目的・手法・結果・考察・結論）が整っているか。
2. 理論の破綻や、前後の論理的な矛盾がないか。
3. 専門家として、説明が不十分な箇所や飛躍している箇所はないか。

以下のJSON形式で、修正が必要な箇所のみ出力してください。
{
  "cor": [
    {
      "o": "修正対象となる原文のフレーズ（完全一致）",
      "c": "改善後の表現または構成案",
      "r": "【構成・論理】指摘の理由（例：論理の飛躍、構成の不足など）"
    }
  ]
}
"""
        return self._call_ai(system_content, text, temperature=0.3)

    def _run_terminology_pass(self, text: str) -> List[Dict[str, str]]:
        """専門用語の表記揺れを統一するパス。"""
        system_content = """あなたはプロの校正者です。
文章全体をスキャンし、専門用語や固有名称の「表記揺れ」を特定して統一してください。

例:
- サーバ / サーバー
- ユーザ / ユーザー
- メソッド / 関数の混在
- Aという用語が場所によってBと呼ばれている

統一ルール：一般的、または文書内で優勢な方に合わせます。
以下のJSON形式で出力してください。
{
  "cor": [
    {
      "o": "揺れている表記（修正前）",
      "c": "統一後の正確な表記",
      "r": "【用語統一】表記揺れの解消"
    }
  ]
}
"""
        return self._call_ai(system_content, text, temperature=0.2)

    def _run_detail_pass(self, text: str) -> List[Dict[str, str]]:
        """従来のチャンク分割による詳細校正。"""
        paragraphs = self._split_into_paragraphs(text)
        chunks = self._make_chunks(paragraphs)
        
        detail_corrections = []
        for i, chunk in enumerate(chunks):
            print(f"  チャンク {i+1}/{len(chunks)} 処理中...")
            system_content = f"""{self.system_prompt}
            
以下のJSON形式で、誤字脱字、文法、てにをはを修正してください。
{{
  "cor": [
    {{
      "o": "原文",
      "c": "修正後",
      "r": "修正理由"
    }}
  ]
}}
"""
            corrections = self._call_ai(system_content, chunk, temperature=0.3)
            detail_corrections.extend(corrections)
        return detail_corrections

    def _split_into_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split('\n') if p.strip()]

    def _make_chunks(self, paragraphs: List[str]) -> List[str]:
        chunks = []
        current_chunk = []
        current_length = 0
        for para in paragraphs:
            if len(para) > self.max_chunk_chars:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                for i in range(0, len(para), self.max_chunk_chars):
                    chunks.append(para[i:i+self.max_chunk_chars])
                continue
            if current_length + len(para) > self.max_chunk_chars:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [para]
                current_length = len(para)
            else:
                current_chunk.append(para)
                current_length += len(para)
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return chunks

    def _call_ai(self, system_prompt: str, text: str, temperature: float = 0.3) -> List[Dict[str, str]]:
        """AI APIを呼び出す共通メソッド。"""
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "user", "content": f"{system_prompt}\n\n--- 添削対象テキスト ---\n{text}"}
            ],
            "temperature": temperature
        }

        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                timeout=120 # 処理が複数パスになるため、少し長めに設定
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content_str = result["choices"][0]["message"]["content"]
                
                # Markdownタグの除去
                content_str = re.sub(r'^```json\s*|\s*```$', '', content_str.strip(), flags=re.MULTILINE)
                
                try:
                    parsed_content = json.loads(content_str)
                except json.JSONDecodeError:
                    # JSONとして不完全な場合の簡易的なリカバリ（必要に応じて）
                    print("JSONデコードエラー。レスポンスをスキップします。")
                    return []
                
                corrections = []
                items = parsed_content.get("cor") or parsed_content.get("corrections") or []
                
                for item in items:
                    corrections.append({
                        "original": item.get("o") or item.get("original", ""),
                        "corrected": item.get("c") or item.get("corrected", ""),
                        "reason": item.get("r") or item.get("reason", "")
                    })
                return corrections
            return []

        except Exception as e:
            print(f"AIリクエストエラー: {e}")
            return []
