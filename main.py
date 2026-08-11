import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform

class InventoryApp(App):
    def build(self):
        # طلب صلاحيات التخزين عند الفتح
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        self.title = "Inventory App"
        
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # زر تحميل الملف من مجلد التنزيلات
        self.btn_load = Button(
            text="Load inventory.xlsx from Download",
            size_hint_y=None,
            height=120,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.btn_load.bind(on_press=self.load_from_download)
        root_layout.add_widget(self.btn_load)
        
        # تسمية لحالة الملف أو الرسائل
        self.lbl_status = Label(
            text="Put 'inventory.xlsx' in your Download folder, then click the button.",
            size_hint_y=None,
            height=80,
            text_size=(700, None)
        )
        self.lbl_status.bind(size=lambda s, w: setattr(s, 'text_size', (w, None)))
        root_layout.add_widget(self.lbl_status)
        
        # منطقة عرض البيانات مع إمكانية التمرير
        self.data_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_layout)
        root_layout.add_widget(scroll)
        
        return root_layout

    def load_from_download(self, instance):
        try:
            self.data_layout.clear_widgets()
            
            # تحديد مسار ملف الإكسل تلقائياً حسب الجهاز
            if platform == 'android':
                file_path = '/storage/emulated/0/Download/inventory.xlsx'
            else:
                file_path = 'inventory.xlsx'  # للتجربة على الكمبيوتر
            
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                self.lbl_status.text = "File not found in Download folder!\nPlease place 'inventory.xlsx' in Download."
                return

            # قراءة ملف الإكسل
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
                    
            self.lbl_status.text = f"Successfully loaded {row_count} rows from Download!"
        except Exception as e:
            self.lbl_status.text = f"Error: {str(e)}"

if __name__ == '__main__':
    InventoryApp().run()
