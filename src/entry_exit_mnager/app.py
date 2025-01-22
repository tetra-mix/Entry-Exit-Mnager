import requests
import flet as ft
from smartcard.System import readers

def send_request(idm, counter = 0):
    if(counter == 0):
        url = f"https://script.google.com/macros/s/AKfycbzM4czXSMWQpafQiOewArYOrBW-QHf5nukrnmJs3GKwaaLYDt1HcdXEWKPyHT-9ibbViw/exec?uuid={idm}&io=1"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            print("Request successful!")
            print("Response Data:")
            print(response.text)
            return response.text 
        else:
            print(f"Request failed with status code: {response.status_code}")
            return "Request failed with status code: {response.status_code}"
    else:
        url = f"https://script.google.com/macros/s/AKfycbzM4czXSMWQpafQiOewArYOrBW-QHf5nukrnmJs3GKwaaLYDt1HcdXEWKPyHT-9ibbViw/exec?uuid={idm}&io=0&people={counter}"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            print("Request successful!")
            print("Response Data:")
            print(response.text)
            return response.text 
        else:
            print(f"Request failed with status code: {response.status_code}")
            return "Request failed with status code: {response.status_code}"

def get_felica_idm():
    try:
        # 利用可能なリーダーを取得
        available_readers = readers()
        if not available_readers:
            return "No smart card readers found."

        # 最初のリーダーを使用
        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()
        print(reader)

        # FeliCa Polling コマンドを送信
        # 00:FF:FF:00:00 はデフォルトの FeliCa Polling コマンド
        # 00 (Command code) | FF FF (System Code) | 00 (Request code)
        GET_IDM_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        response, sw1, sw2 = connection.transmit(GET_IDM_APDU)

        if sw1 == 0x90 and sw2 == 0x00:
            idm = response
            idm_data = ''.join(format(byte, '02X') for byte in idm)
            print("カードのIDm:", idm_data)
            
        else:
            idm_data = "Error: cant't get card idm"
            print("カードのIDmを取得できませんでした")
        
        connection.disconnect()
        return idm_data

    except Exception as e:
        return f"Error: {str(e)}"

def main(page: ft.Page):
    
    page.title = "Smart Card Reader with Flet and pyscard"
    
    output_label = ft.Text(value="", size=30, color=ft.Colors.RED_700)
    
    people_text = ft.Text(value=f"1", size=30)
    def people_add(e):
        people_text.value = str(int(people_text.value) + 1)
        people_text.update()

    def people_sub(e):
        if int(people_text.value) <= 1:
            return
        people_text.value = str(int(people_text.value) - 1)
        people_text.update()

    spacer = ft.Container(
        padding=20,
    )

    
    dlg_entry = ft.AlertDialog(
        modal=True,
        title=ft.Text("質問に答えてからICカードをかざしてください", size=30),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("何人で来ましたか?", size=25),
                        spacer,
                        people_text,
                        ft.Text("人", size=25),
                        spacer,
                        ft.FilledButton("+", bgcolor=ft.Colors.BLUE_700, on_click=people_add),
                        ft.FilledButton("-", bgcolor=ft.Colors.RED_700, on_click=people_sub),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=200,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            height=200,
        ),
        actions=[
            ft.Row(
                [
                    ft.FilledButton(
                        "ICカードを読み取る", 
                        width=180,
                        bgcolor=ft.Colors.GREEN_700, 
                        on_click=lambda e: (
                            setattr(output_label, 'value', send_request(get_felica_idm(), int(people_text.value))),
                            page.update(),
                            page.close(dlg_entry)
                        )
                    ),
                    spacer,
                    ft.FilledButton(
                        "閉じる", 
                        width=100,
                        bgcolor=ft.Colors.PURPLE_300, 
                        on_click=lambda e: (
                            page.close(dlg_entry)
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dlg_exit = ft.AlertDialog(
        modal=True,
        title=ft.Text("ICカードを置いてください", size=30),
        actions=[
            ft.Row(
                [
                    ft.FilledButton(
                        "ICカードを読み取る", 
                        width=180,
                        bgcolor=ft.Colors.GREEN_700, 
                        on_click=lambda e: (
                            setattr(output_label, 'value', send_request(get_felica_idm(), 0)),
                            page.update(),
                            page.close(dlg_exit)
                        )
                    ),
                    spacer,
                    ft.FilledButton(
                        "閉じる", 
                        width=100,
                        bgcolor=ft.Colors.PURPLE_300, 
                        on_click=lambda e: (
                            page.close(dlg_exit)
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


    page.appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.INFO,
            icon_color=ft.Colors.WHITE,
            icon_size=45,
        ),
        leading_width=60,
        title=ft.Text("起業家工房 IC 入退室記録", size=30),
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_500,
        center_title=True,
    )
    
    left_button = ft.ElevatedButton(
        content=ft.Text(value="入室", color=ft.Colors.WHITE, size=90),
        expand=True,
        width= page.width/2 - 100,
        height=page.width/2 - 100,
        bgcolor=ft.Colors.BLUE_500,
        on_click=lambda e: page.open(dlg_entry),
    )

    right_button = ft.ElevatedButton(
        content=ft.Text(value="退室", color=ft.Colors.WHITE, size=90),
        expand=True,
        width= page.width/2 - 100,
        height=page.width/2 - 100,
        bgcolor=ft.Colors.RED_500,
        on_click=lambda e: page.open(dlg_exit),
        #on_click=lambda e: (setattr(output_label, 'value', get_card_info()), output_label.update()),
    )

    left_button_container  = ft.Container(
        content=left_button,
        margin=50,
        padding=20,
        alignment=ft.alignment.center,
        width= page.height/1.5 - 100,
        height= page.height/1.5 - 100,
        border_radius=10,
    )

    right_button_container  = ft.Container(
        content=right_button,
        margin=50,
        padding=20,
        alignment=ft.alignment.center,
        width=page.height/1.5 - 100,
        height=page.height/1.5 - 100,
        border_radius=10,
    )

    page.add(
        ft.Column(
            [
                ft.Container(
                    padding=40,
                ),
                ft.Row(
                    [
                        ft.Text(
                            value="ICカードを置いてから操作してください！",
                            size=35,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        output_label,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                [
                    left_button_container,
                    right_button_container,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        ),
    )
    
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.SETTINGS,
        bgcolor=ft.Colors.LIME_300,
        on_click=(),
    )

    

    # レイアウトに追加
    # 画面サイズ変更時に実行される関数
    def on_resized(e):
        left_button_container.width = page.height/1.5 - 100
        left_button_container.height = page.height/1.5 - 100
        right_button_container.width = page.height/1.5 - 100
        right_button_container.height = page.height/1.5 - 100
        left_button.width = page.width/2 - 100
        left_button.height = page.width/2 - 100
        right_button.width = page.width/2 - 100
        right_button.height = page.width/2 - 100
        page.update()

    page.on_resized = on_resized

    

# アプリの実行
if __name__ == "__main__":
    ft.app(target=main)
