import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform
from plyer import filechooser

class InventoryApp(App):
    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        self.title = "Inventory App"
        
        # التصميم الرئيسي
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # زر اختيار الملف
        self.btn_select = Button(
            text="Select Excel File",
            size_hint_y=None,
            height=120,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.btn_select.bind(on_press=self.open_file_chooser)
        root_layout.add_widget(self.btn_select)
        
        # تسمية الحالة
        self.lbl_status = Label(
            text="Please select an Excel file to view data",
            size_hint_y=None,
            height=60
        )
        root_layout.add_widget(self.lbl_status)
        
        # منطقة عرض بيانات الإكسل مع إمكانية التمرير
        self.data_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_layout)
        root_layout.add_widget(scroll)
        
        return root_layout

    def open_file_chooser(self, instance):
        filechooser.open_file(
            on_selection=self.handle_selection,
            filters=[("Excel Files", "*.xlsx", "*.xls")]
        )

    def handle_selection(self, selection):
        if selection:
            file_path = selection[0]
            self.btn_select.text = "File Selected Successfully"
            self.load_excel_data(file_path)

    def load_excel_data(self, file_path):
        try:
            self.data_layout.clear_widgets()
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            
            row_count = 0
            for row in sheet.iter_rows(values_only=True):
                row_text = " | ".join([str(cell) for cell in row if cell is not None])
                if row_text.strip():
                    lbl = Label(
                        text=row_text,
                        size_hint_y=None,
                        height=50,
                        color=(1, 1, 1, 1)
                    )
                    self.data_layout.add_widget(lbl)
                    row_count += 1
                    
            self.lbl_status.text = f"Loaded {row_count} rows successfully"
        except Exception as e:
            self.lbl_status.text = f"Error reading file: {str(e)}"

if __name__ == '__main__':
    InventoryApp().run()
