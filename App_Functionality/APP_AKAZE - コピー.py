    err_dlg = ft.AlertDialog(
        title=ft.Text("エラー"),
        modal=True,
        content=ft.Text("ダウンロード中にエラーが発生しました。"),
        actions=[
            ft.TextButton("閉じる",on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )