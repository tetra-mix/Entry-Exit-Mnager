import flet as ft
from smartcard.System import readers
from smartcard.util import toHexString

def get_card_info():
    try:
        # 利用可能なリーダーを取得
        available_readers = readers()
        if not available_readers:
            return "No smart card readers found."
        
        # 最初のリーダーを使用
        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()
        
        # ATRを取得
        atr = connection.getATR()
        atr_hex = toHexString(atr)
        return f"Connected to: {reader}\nATR: {atr_hex}"
    except Exception as e:
        return f"Error: {str(e)}"

def main(page: ft.Page):
    page.title = "Smart Card Reader with Flet and pyscard"
    
    # ラベルとボタン
    output_label = ft.Text(value="Click the button to check for a smart card.")
    read_button = ft.ElevatedButton(
        text="Read Card Info",
        on_click=lambda e: (setattr(output_label, 'value', get_card_info()), output_label.update())
    )

    # レイアウトに追加
    page.add(output_label, read_button)

# アプリの実行
if __name__ == "__main__":
    ft.app(target=main)
