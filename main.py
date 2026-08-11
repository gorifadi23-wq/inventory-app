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
from kivy.utils import platform
from plyer import filechooser

class InventoryApp(App):
    def build(self):
        # 1. طلب الأذونات تلقائياً عند فتح التطبيق على الأندرويد
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        self.title = "مستودع المواد - البحث الذكي"
        
        # التصميم الرئيسي
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # زر اختيار ملف الإكسل من الهاتف
        self.choose_file_btn = Button(
            text="اختر ملف الإكسل من الهاتف",
            size_hint_y=None,
            height=100,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.choose_file_btn.bind(on_press=self.open_file_chooser)
        self.main_layout.add_widget(self.choose_file_btn)
        
        # تسمية لحالة الملف أو النتائج
        self.status_label = Label(text="الرجاء اختيار ملف الإكسل للبدء", size_hint_y=None, height=50)
        self.main_layout.add_widget(self.status_label)

        return self.main_layout

    def open_file_chooser(self, instance):
        # فتح مستعرض الملفات في الهاتف لاختيار ملف إكسل
        filechooser.open_file(
            on_selection=self.handle_selection,
            filters=[("Excel Files", "*.xlsx", "*.xls")]
        )

    def handle_selection(self, selection):
        if selection:
            file_path = selection[0]
            self.choose_file_btn.text = f"الملف: {os.path.basename(file_path)}"
            # استدعاء دالة تحميل الإكسل بالمسار الجديد
            self.load_excel_data(file_path)

    def load_excel_data(self, file_path):
        try:
            wb = openpyxl.load_workbook(file_path)
            self.status_label.text = "تم تحميل ملف الإكسل بنجاح!"
            # ضع هنا باقي كود عرض البيانات الخاص بك
        except Exception as e:
            self.status_label.text = f"خطأ في قراءة الملف: {e}"

if __name__ == '__main__':
    InventoryApp().run()
