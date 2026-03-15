import os
import json

CONFIG_FILE = "config.json"

class ConfigManager:
    """
    アプリケーション全体の設定（エンドポイントURL、モデル、プロンプトなど）を管理するクラス。
    """
    def __init__(self):
        self.config = {
            "custom_ai_url": "",
            "custom_ai_api_key": "",
            "openai_model": "gpt-4o-mini",
            "system_prompt": "あなたはプロの編集者・ライターです。提供された文章の誤字脱字、文法の誤り、不自然な表現を修正してください。修正箇所とその理由を簡潔に出力してください。"
        }
        self.load_config()

    def load_config(self):
        """ファイルから設定を読み込みます。"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"設定の読み込みエラー: {e}")

    def save_config(self):
        """設定をファイルに保存します。"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"設定の保存エラー: {e}")

    def get(self, key, default=None):
        """指定したキーの設定値を取得します。"""
        return self.config.get(key, default)

    def set(self, key, value):
        """設定値を更新し、ファイルに保存します。"""
        self.config[key] = value
        self.save_config()

# アプリケーション全体で共有するインスタンス
config_manager = ConfigManager()
