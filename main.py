import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest

class InventoryApp(App):
    def build(self):
        self.title = "Inventory App"
        
        # إنشاء مسار آمن ومخفي داخل التطبيق لحفظ الإكسل بدون الحاجة لصلاحيات الأندرويد
        self.file_path = os.path.join(self.user_data_dir, 'inventory.xlsx')
        
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # زر التحديث السحري
        self.btn_update = Button(
            text="Update Data (Download new Excel)",
            size_hint_y=None,
            height=120,
            background_color=(0.2, 0.8, 0.2, 1)  # لون أخضر للزر
        )
        self.btn_update.bind(on_press=self.download_update)
        root_layout.add_widget(self.btn_update)
        
        # تسمية لحالة التطبيق
        self.lbl_status = Label(
            text="Welcome! Checking for data...",
            size_hint_y=None,
            height=60
        )
        root_layout.add_widget(self.lbl_status)
        
        # منطقة عرض البيانات
        self.data_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_layout)
        root_layout.add_widget(scroll)
        
        # التحقق مما إذا كان الملف موجوداً مسبقاً لعرضه مباشرة
        if os.path.exists(self.file_path):
            self.load_excel_data()
        else:
            self.lbl_status.text = "No data found. Please click Update!"
            
        return root_layout

    def download_update(self, instance):
        self.lbl_status.text = "Downloading new data... Please wait."
        self.btn_update.disabled = True
        
        # هذا هو الرابط المباشر لملف الإكسل من مستودعك الذي رأيته في صورتك
        url = "https://raw.githubusercontent.com/gorifadi23-wq/inventory-app/main/inventory.xlsx"
        
        UrlRequest(
            url,
            on_success=self.on_download_success,
            on_error=self.on_download_error,
            on_failure=self.on_download_error,
            file_path=self.file_path
        )

    def on_download_success(self, req, result):
        self.btn_update.disabled = False
        self.lbl_status.text = "Update Downloaded Successfully!"
        self.load_excel_data()

    def on_download_error(self, req, error):
        self.btn_update.disabled = False
        self.lbl_status.text = "Error! Please check your internet connection."

    def load_excel_data(self):
        try:
            self.data_layout.clear_widgets()
            wb = openpyxl.load_workbook(self.file_path)
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
                    
            self.lbl_status.text = f"Loaded {row_count} rows successfully!"
        except Exception as e:
            self.lbl_status.text = f"Error reading file: {str(e)}"

if __name__ == '__main__':
    InventoryApp().run()
