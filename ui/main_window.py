import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import threading
from core.docx_editor import DocxEditor
from core.methods.rule_based import RuleBasedProofreader
from core.methods.ai_server import AIServerProofreader

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Word AI 添削アプリ")
        self.geometry("600x550")

        # UI要素の配置
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 手法選択
        self.label_method = ctk.CTkLabel(self, text="添削手法:")
        self.label_method.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.combo_method = ctk.CTkComboBox(
            self, 
            values=["ルールベース", "AIサーバー"],
            width=200,
            command=self.on_method_change
        )
        self.combo_method.grid(row=0, column=0, padx=(150, 20), pady=(20, 0), sticky="w")
        self.combo_method.set("ルールベース") # デフォルト値

        # API URL/キー (手法によって切り替え)
        self.label_api_url = ctk.CTkLabel(self, text="AIサーバー URL:")
        self.label_api_url.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.entry_api_url = ctk.CTkEntry(self, placeholder_text="http://localhost:5000/api/proofread", width=400)
        self.entry_api_url.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # 初期状態ではAIサーバーURLを無効化
        self.entry_api_url.configure(state="disabled")

        # 環境変数から初期値取得 (AI_SERVER_URL があれば設定)
        env_url = os.getenv("AI_SERVER_URL", "")
        if env_url:
            self.entry_api_url.insert(0, env_url)

        # Excelルールファイル選択 (ルールベース用)
        self.label_rule_file = ctk.CTkLabel(self, text="ルール定義Excelファイル:")
        self.label_rule_file.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.frame_rule_file = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_rule_file.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.frame_rule_file.grid_columnconfigure(0, weight=1)

        self.entry_rule_file_path = ctk.CTkEntry(self.frame_rule_file, placeholder_text="rules.xlsx を選択してください...")
        self.entry_rule_file_path.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_rule_file_path.insert(0, os.path.abspath("rules.xlsx")) # デフォルト値

        self.button_rule_browse = ctk.CTkButton(self.frame_rule_file, text="参照", command=self.browse_rule_file, width=80)
        self.button_rule_browse.grid(row=0, column=1, sticky="e")

        # 対象Wordファイル選択
        self.label_file = ctk.CTkLabel(self, text="添削するWordファイル:")
        self.label_file.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.frame_file = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_file.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_file.grid_columnconfigure(0, weight=1)

        self.entry_file_path = ctk.CTkEntry(self.frame_file, placeholder_text="ファイルを選択してください...")
        self.entry_file_path.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.button_browse = ctk.CTkButton(self.frame_file, text="参照", command=self.browse_file, width=80)
        self.button_browse.grid(row=0, column=1, sticky="e")

        # 実行ボタン
        self.button_run = ctk.CTkButton(self, text="添削を開始する", command=self.start_processing_thread, height=40)
        self.button_run.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

        # ログ表示
        self.textbox_log = ctk.CTkTextbox(self, height=150)
        self.textbox_log.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_log.insert("0.0", "待機中...\n")
        self.textbox_log.configure(state="disabled")

        # プログレスバー
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progressbar.set(0)

    def on_method_change(self, choice):
        """添削手法が変更されたときの処理"""
        if choice == "AIサーバー":
            self.entry_api_url.configure(state="normal")
            self.entry_rule_file_path.configure(state="disabled")
            self.button_rule_browse.configure(state="disabled")
        else:
            self.entry_api_url.configure(state="disabled")
            self.entry_rule_file_path.configure(state="normal")
            self.button_rule_browse.configure(state="normal")

    def browse_rule_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if filename:
            self.entry_rule_file_path.delete(0, tk.END)
            self.entry_rule_file_path.insert(0, filename)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
        if filename:
            self.entry_file_path.delete(0, tk.END)
            self.entry_file_path.insert(0, filename)

    def log(self, message):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert(tk.END, f"{message}\n")
        self.textbox_log.see(tk.END)
        self.textbox_log.configure(state="disabled")

    def start_processing_thread(self):
        method_name = self.combo_method.get()
        api_url = self.entry_api_url.get()
        file_path = self.entry_file_path.get()
        rule_path = self.entry_rule_file_path.get()

        if method_name == "AIサーバー" and not api_url:
            messagebox.showerror("エラー", "AIサーバーのURLを入力してください。")
            return
        if method_name == "ルールベース" and (not rule_path or not os.path.exists(rule_path)):
            messagebox.showerror("エラー", "有効なルール定義Excelファイルを選択してください。")
            return
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("エラー", "有効なWordファイルを選択してください。")
            return

        self.button_run.configure(state="disabled")
        self.progressbar.set(0.1)
        
        thread = threading.Thread(target=self.process_file, args=(method_name, api_url, rule_path, file_path))
        thread.start()

    def process_file(self, method_name, api_url, rule_path, file_path):
        try:
            self.log(f"ファイルを読み込み中: {os.path.basename(file_path)}")
            editor = DocxEditor(file_path)
            text = editor.get_text()
            
            self.log(f"添削手法: {method_name}")
            self.progressbar.set(0.4)
            
            if method_name == "ルールベース":
                self.log(f"ルールベースの添削を実行中... ({os.path.basename(rule_path)})")
                proofreader = RuleBasedProofreader(excel_path=rule_path)
            elif method_name == "AIサーバー":
                self.log(f"AIサーバー ({api_url}) へリクエスト送信中...")
                proofreader = AIServerProofreader(endpoint_url=api_url)
            else:
                raise ValueError("不明な添削手法です。")
                
            corrections = proofreader.proofread(text)
            
            if not corrections:
                self.log("修正箇所は見つかりませんでした。")
            else:
                self.log(f"{len(corrections)}件の修正箇所を適用中...")
                self.progressbar.set(0.7)
                editor.apply_corrections(corrections)
            
            output_path = file_path.replace(".docx", "_添削済み.docx")
            editor.save(output_path)
            
            self.progressbar.set(1.0)
            self.log(f"完了しました！保存先: {output_path}")
            messagebox.showinfo("完了", f"添削が完了しました。\n保存先: {output_path}")
            
        except Exception as e:
            self.log(f"エラーが発生しました: {str(e)}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")
        
        finally:
            self.button_run.configure(state="normal")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
