import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import threading
from core.docx_editor import DocxEditor
from core.openai_client import OpenAIClient

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Word AI 添削アプリ")
        self.geometry("600x450")

        # UI要素の配置
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # APIキー
        self.label_api_key = ctk.CTkLabel(self, text="OpenAI APIキー:")
        self.label_api_key.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.entry_api_key = ctk.CTkEntry(self, placeholder_text="sk-...", width=400, show="*")
        self.entry_api_key.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        # 環境変数から初期値取得
        env_key = os.getenv("OPENAI_API_KEY", "")
        if env_key:
            self.entry_api_key.insert(0, env_key)

        # ファイル選択
        self.label_file = ctk.CTkLabel(self, text="添削するWordファイル:")
        self.label_file.grid(row=2, column=0, padx=20, pady=(0, 0), sticky="w")
        
        self.frame_file = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_file.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_file.grid_columnconfigure(0, weight=1)

        self.entry_file_path = ctk.CTkEntry(self.frame_file, placeholder_text="ファイルを選択してください...")
        self.entry_file_path.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.button_browse = ctk.CTkButton(self.frame_file, text="参照", command=self.browse_file, width=80)
        self.button_browse.grid(row=0, column=1, sticky="e")

        # 実行ボタン
        self.button_run = ctk.CTkButton(self, text="添削を開始する", command=self.start_processing_thread, height=40)
        self.button_run.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # ログ表示
        self.textbox_log = ctk.CTkTextbox(self, height=150)
        self.textbox_log.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_log.insert("0.0", "待機中...\n")
        self.textbox_log.configure(state="disabled")

        # プログレスバー
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progressbar.set(0)

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
        api_key = self.entry_api_key.get()
        file_path = self.entry_file_path.get()

        if not api_key:
            messagebox.showerror("エラー", "APIキーを入力してください。")
            return
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("エラー", "有効なWordファイルを選択してください。")
            return

        self.button_run.configure(state="disabled")
        self.progressbar.set(0.1)
        
        thread = threading.Thread(target=self.process_file, args=(api_key, file_path))
        thread.start()

    def process_file(self, api_key, file_path):
        try:
            self.log(f"ファイルを読み込み中: {os.path.basename(file_path)}")
            editor = DocxEditor(file_path)
            text = editor.get_text()
            
            self.log("OpenAI APIで添削中（しばらく時間がかかります）...")
            self.progressbar.set(0.4)
            
            client = OpenAIClient(api_key=api_key)
            corrections = client.proofread(text)
            
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
