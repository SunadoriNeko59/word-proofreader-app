import json
import urllib.request
import urllib.error
from typing import List, Dict
from core.methods.base import BaseProofreader
from core.config import config_manager

class CustomAPIProofreader(BaseProofreader):
    """
    社内AIサーバー等の独自エンドポイントを直接呼び出して添削を行うクラス
    """
    def __init__(self):
        super().__init__()
        self.endpoint_url = config_manager.get("custom_ai_url", "")
        self.api_key = config_manager.get("custom_ai_api_key", "")
        self.model = config_manager.get("openai_model", "gpt-4o-mini")
        self.system_prompt = config_manager.get("system_prompt", "")
        
        if not self.endpoint_url:
            raise ValueError("AIエンドポイントURLが設定されていません。設定画面から登録してください。")

    def proofread(self, text: str) -> List[Dict[str, str]]:
        """
        カスタムAIエンドポイントにテキストを送信し、添削結果を受け取ります。
        """
        print(f"--- カスタムAI API ({self.endpoint_url}) へリクエスト送信 ---")
        
        system_content = f"""{self.system_prompt}
        
以下のJSONフォーマット（スキーマ）に従って、添削結果を必ず出力してください:
{{
  "corrections": [
    {{
      "original": "修正前の文字列（与えられた原文と完全に一致する部分文字列であること）",
      "corrected": "修正後の文字列",
      "reason": "修正の理由"
    }}
  ]
}}
修正箇所が一つもない場合は、"corrections"を空のリスト [ ] としてください。
"""
        
        # OpenAI互換APIを想定したペイロード
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3
        }

        data = json.dumps(payload).encode('utf-8')
        
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        req = urllib.request.Request(
            self.endpoint_url,
            data=data,
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                response_body = response.read().decode('utf-8')
                result = json.loads(response_body)
                
                # OpenAI互換レスポンスモデルのパース
                if "choices" in result and len(result["choices"]) > 0:
                    content_str = result["choices"][0]["message"]["content"]
                    parsed_content = json.loads(content_str)
                    
                    if "corrections" in parsed_content:
                        return parsed_content["corrections"]
                return []

        except urllib.error.URLError as e:
            print(f"APIサーバーへの接続エラー: {e}")
            raise Exception(f"AIサーバーへのリクエストに失敗しました:\n{e}")
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            raise Exception("AIからの返答をパースできませんでした。プロンプトを見直してください。")
        except Exception as e:
            print(f"予期せぬAPIエラー: {e}")
            raise Exception(f"カスタムAI APIでの添削中にエラーが発生しました:\n{str(e)}")
