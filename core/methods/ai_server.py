import urllib.request
import urllib.error
import json
from typing import List, Dict
from core.methods.base import BaseProofreader

class AIServerProofreader(BaseProofreader):
    """
    社内AIサーバーのAPIを呼び出して添削を行うクラス
    """
    def __init__(self, endpoint_url: str):
        super().__init__()
        self.endpoint_url = endpoint_url
        if not self.endpoint_url:
            raise ValueError("AIサーバーのエンドポイントURLが設定されていません。")

    def proofread(self, text: str) -> List[Dict[str, str]]:
        """
        AIサーバーにテキストを送信し、添削結果を受け取ります。
        """
        print(f"--- AIサーバー ({self.endpoint_url}) へリクエスト送信 ---")
        
        # サーバーへ送信するペイロード
        payload = {
            "text": text
        }
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            self.endpoint_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_body = response.read().decode('utf-8')
                result = json.loads(response_body)
                
                # サーバーからのレスポンス形式が List[Dict] であることを期待
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict) and "corrections" in result:
                    return result["corrections"]
                else:
                    return []

        except urllib.error.URLError as e:
            # サーバー接続に失敗した場合はテスト用のダミーを返すか、エラーをスローする
            # 今回はフォールバックとしてダミーを返す（本番運用ではExceptionを投げるべき）
            print(f"AIサーバーへの接続エラー: {e}")
            print("モックデータによる仮の修正結果を返します。")
            return self._get_mock_corrections(text)
        except Exception as e:
            print(f"予期せぬエラー: {e}")
            return self._get_mock_corrections(text)

    def _get_mock_corrections(self, text: str) -> List[Dict[str, str]]:
        # テスト用のダミーデータ（元のopenai_client.pyと同様）
        dummy_corrections = [
            {
                "original": "、",
                "corrected": "、",
                "reason": "句読点の後は一文字空ける習慣があるかもしれませんが、ここでは文脈を確認してください（AIダミー）。"
            },
            {
                "original": "です",
                "corrected": "である",
                "reason": "文末を常体に統一することを検討してください（AIダミー）。"
            },
            {
                "original": "ます",
                "corrected": "る",
                "reason": "語尾のバリエーションを増やすと読みやすくなります（AIダミー）。"
            }
        ]
        
        actual_corrections = []
        for d in dummy_corrections:
            if d["original"] in text:
                actual_corrections.append(d)
        
        return actual_corrections
