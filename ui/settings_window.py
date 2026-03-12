import customtkinter as ctk
from core.config import config_manager

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("設定 - 社内AI (カスタムエンドポイント)")
        self.geometry("500x400")
        
        # モーダルダイアログとして動作させる
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # API Key -> Custom AI Endpoint URL
        self.label_ai_url = ctk.CTkLabel(self, text="AI エンドポイント URL:")
        self.label_ai_url.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="e")
        
        self.entry_ai_url = ctk.CTkEntry(self)
        self.entry_ai_url.grid(row=0, column=1, padx=(0, 20), pady=(20, 10), sticky="ew")
        
        # Model
        self.label_model = ctk.CTkLabel(self, text="使用モデル:")
        self.label_model.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        
        self.combo_model = ctk.CTkComboBox(self, values=["gpt-4o-mini", "gpt-4o"])
        self.combo_model.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")

        # System Prompt
        self.label_prompt = ctk.CTkLabel(self, text="システムプロンプト:")
        self.label_prompt.grid(row=2, column=0, padx=20, pady=10, sticky="ne")
        
        self.textbox_prompt = ctk.CTkTextbox(self, height=150)
        self.textbox_prompt.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="nsew")

        # 現在の設定を読み込み
        self.load_settings()

        # Save Button
        self.button_save = ctk.CTkButton(self, text="保存", command=self.save_settings)
        self.button_save.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def load_settings(self):
        """設定をUIに反映します。"""
        self.entry_ai_url.insert(0, config_manager.get("custom_ai_url", "http://127.0.0.1:8000/v1/chat/completions"))
        self.combo_model.set(config_manager.get("openai_model", "gpt-4o-mini"))
        
        prompt = config_manager.get("system_prompt", "")
        self.textbox_prompt.insert("0.0", prompt)

    def save_settings(self):
        """UIの入力内容を設定に保存します。"""
        config_manager.set("custom_ai_url", self.entry_ai_url.get())
        config_manager.set("openai_model", self.combo_model.get())
        config_manager.set("system_prompt", self.textbox_prompt.get("0.0", "end").strip())
        
        self.destroy()
