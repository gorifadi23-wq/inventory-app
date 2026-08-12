import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class InventoryApp(App):
    def build(self):
        self.title = "Inventory App"
        
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # تسمية لحالة التطبيق وعرض عدد الصفوف
        self.lbl_status = Label(
            text="Loading inventory data...",
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
        
        # تحميل الملف مباشرة من حزمة التطبيق
        self.load_bundled_excel()
        
        return root_layout

    def load_bundled_excel(self):
        try:
            self.data_layout.clear_widgets()
            
            # مسار الملف المدمج داخل التطبيق
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, 'inventory.xlsx')
            
            if not os.path.exists(file_path):
                self.lbl_status.text = "Error: inventory.xlsx not found in package!"
                return

            # قراءة البيانات
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
                    
            self.lbl_status.text = f"Loaded {row_count} rows successfully!"
        except Exception as e:
            self.lbl_status.text = f"Error: {str(e)}"

if __name__ == '__main__':
    InventoryApp().run()
