import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp, sp  # سر الاحترافية لتكييف الأحجام مع شاشات الهواتف

import arabic_reshaper
from bidi.algorithm import get_display

# خلفية رمادية فاتحة عصرية
Window.clearcolor = (0.94, 0.94, 0.96, 1)

class HeaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(75) # ارتفاع مناسب للشريط العلوي
        self.padding = dp(15)
        with self.canvas.before:
            Color(0.12, 0.35, 0.71, 1) # أزرق احترافي
            self.rect = Rectangle()
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class CardLayout(BoxLayout):
    def __init__(self, text, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(90) # ارتفاع أكبر للبطاقة لراحة العين
        self.padding = [dp(15), dp(10), dp(15), dp(10)]
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            # حواف دائرية ناعمة للبطاقة
            self.rect = RoundedRectangle(radius=[dp(12)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # معالجة النص العربي
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        self.lbl = Label(
            text=bidi_text,
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.15, 0.15, 0.15, 1),
            font_size=sp(16), # حجم خط ديناميكي كبير
            halign='right',
            valign='middle'
        )
        # ربط حجم النص بحجم البطاقة لمنع الخروج عن الحدود (التفاف تلقائي)
        self.lbl.bind(size=self.update_text_size)
        self.add_widget(self.lbl)

    def update_text_size(self, instance, size):
        instance.text_size = (size[0], size[1])

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FadiInventoryApp(App):
    def build(self):
        self.title = "Inventory App"
        self.all_data = []
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')
        
        main_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # 1. الشريط العلوي
        header = HeaderLayout()
        header_title = Label(
            text="INVENTORY SYSTEM", 
            color=(1, 1, 1, 1), 
            bold=True, 
            font_size=sp(20)
        )
        header.add_widget(header_title)
        main_box.add_widget(header)
        
        # 2. مربع البحث الذكي (تصميم احترافي غير مقطوع)
        search_hint = get_display(arabic_reshaper.reshape('بحث ذكي عن المواد...'))
        self.search_input = TextInput(
            hint_text=search_hint,
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None,
            height=dp(60), # ارتفاع كافي جداً
            font_size=sp(18), # خط كبير للكتابة
            multiline=False,
            padding=[dp(15), dp(15), dp(15), dp(15)],
            halign='right',
            background_normal='', # إزالة الظل الافتراضي المزعج
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.12, 0.35, 0.71, 1)
        )
        self.search_input.bind(text=self.on_search_change)
        
        # حاوية لمربع البحث لإعطائه هوامش جانبية
        search_container = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(15), 0, dp(15), 0])
        search_container.add_widget(self.search_input)
        main_box.add_widget(search_container)
        
        # 3. شريط الحالة
        status_text = get_display(arabic_reshaper.reshape("جاري تحضير الواجهة..."))
        self.info_label = Label(
            text=status_text,
            size_hint_y=None, 
            height=dp(30), 
            color=(0.12, 0.35, 0.71, 1), 
            font_size=sp(16),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto'
        )
        main_box.add_widget(self.info_label)
        
        # 4. شبكة البيانات
        self.data_grid = GridLayout(cols=1, spacing=dp(10), padding=[dp(15), dp(5), dp(15), dp(15)], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_grid)
        main_box.add_widget(scroll)
        
        Clock.schedule_once(self.load_excel_data, 0.5)
        
        return main_box

    def load_excel_data(self, dt):
        msg = arabic_reshaper.reshape("جاري قراءة البيانات...")
        self.info_label.text = get_display(msg)
        
        excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        
        if not os.path.exists(excel_file):
            msg = arabic_reshaper.reshape("خطأ: ملف inventory.xlsx مفقود!")
            self.info_label.text = get_display(msg)
            self.info_label.color = (0.9, 0.1, 0.1, 1)
            return
            
        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = workbook.active
            
            for row in sheet.iter_rows(values_only=True):
                row_values = [str(cell) for cell in row if cell is not None]
                if row_values:
                    self.all_data.append("  |  ".join(row_values))
                    
            self.update_ui("")
                
        except Exception as e:
            self.info_label.text = f"Error: {str(e)[:40]}" 
            self.info_label.color = (0.9, 0.1, 0.1, 1)

    def on_search_change(self, instance, value):
        self.update_ui(value)

    def update_ui(self, search_text):
        self.data_grid.clear_widgets()
        search_terms = search_text.lower().split()
        
        displayed_count = 0
        for item in self.all_data:
            match = True
            item_lower = item.lower()
            
            for term in search_terms:
                if term not in item_lower:
                    match = False
                    break
                    
            if match:
                if displayed_count >= 200:
                    break
                card = CardLayout(text=item, font_path=self.font_path)
                self.data_grid.add_widget(card)
                displayed_count += 1
                
        msg = arabic_reshaper.reshape(f"تم عرض {displayed_count} نتيجة")
        self.info_label.text = get_display(msg)
        self.info_label.color = (0.1, 0.6, 0.1, 1)

if __name__ == '__main__':
    FadiInventoryApp().run()
