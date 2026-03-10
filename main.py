import sys
import os

# core と ui ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"アプリケーションの起動に失敗しました: {e}")

if __name__ == "__main__":
    main()
