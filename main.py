
import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.camera import Camera

class InventoryApp(App):
    def build(self):
        self.title = "مستودع المواد - البحث الذكي"
        self.data = []
        
        # 1. تحميل بيانات الإكسل
        self.load_excel_data()

        # 2. الواجهة الرئيسية
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # حقل البحث النصي
        self.search_input = TextInput(
            hint_text='ادخل اسم المادة أو الكود للبحث...',
            multiline=False,
            font_size='18sp',
            size_hint_y=None,
            height=50
        )
        self.search_input.bind(text=self.on_search_text_change)
        self.main_layout.add_widget(self.search_input)

        # زر تشغيل الكاميرا
        self.cam_btn = Button(
            text='فتح / إغلاق الكاميرا',
            size_hint_y=None,
            height=45,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.cam_btn.bind(on_press=self.toggle_camera)
        self.main_layout.add_widget(self.cam_btn)

        # ويدجت الكاميرا (مخفية افتراضياً)
        self.camera = Camera(play=False, size_hint_y=None, height=200)
        self.camera_active = False

        # منطقة عرض النتائج (جدول قابل للتمرير)
        self.scroll = ScrollView()
        self.results_grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        self.scroll.add_widget(self.results_grid)
        self.main_layout.add_widget(self.scroll)

        # عرض العينة الأولى من البيانات
        self.update_results(self.data[:40])

        return self.main_layout

    def load_excel_data(self):
        # البحث عن ملف الإكسل
        file_names = ['inventory.xlsx', 'data.xlsx', 'items.xlsx']
        target_file = None
        for f in file_names:
            if os.path.exists(f):
                target_file = f
                break

        if target_file:
            try:
                wb = openpyxl.load_workbook(target_file, data_only=True)
                sheet = wb.active
                for row in sheet.iter_rows(values_only=True):
                    if any(row):
                        str_row = [str(cell) if cell is not None else "" for cell in row]
                        self.data.append(str_row)
            except Exception as e:
                print(f"خطأ في قراءة ملف الإكسل: {e}")
        else:
            self.data = [["تنبيه", "لم يتم العثور على ملف inventory.xlsx"]]

    def on_search_text_change(self, instance, value):
        query = value.strip().lower()
        if not query:
            self.update_results(self.data[:40])
            return

        filtered = []
        for row in self.data:
            row_str = " ".join(row).lower()
            if query in row_str:
                filtered.append(row)
                if len(filtered) >= 80:
                    break

        self.update_results(filtered)

    def update_results(self, rows):
        self.results_grid.clear_widgets()

        if not rows:
            lbl = Label(text="لا توجد نتائج مطابقة", size_hint_y=None, height=40, color=(1, 0, 0, 1))
            self.results_grid.add_widget(lbl)
            return

        for row in rows:
            text_line = "  |  ".join(row)
            btn = Button(
                text=text_line,
                size_hint_y=None,
                height=50,
                halign='right',
                valign='middle',
                background_normal='',
                background_color=(0.15, 0.2, 0.25, 1)
            )
            btn.bind(size=btn.setter('text_size'))
            self.results_grid.add_widget(btn)

    def toggle_camera(self, instance):
        if not self.camera_active:
            self.main_layout.add_widget(self.camera, index=2)
            self.camera.play = True
            self.camera_active = True
        else:
            self.camera.play = False
            self.main_layout.remove_widget(self.camera)
            self.camera_active = False

if __name__ == '__main__':
    InventoryApp().run()
