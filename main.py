import os
import threading
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.clock import Clock, mainthread
from kivy.metrics import dp, sp

import arabic_reshaper
from bidi.algorithm import get_display

Window.clearcolor = (0.95, 0.95, 0.97, 1)

def format_arabic(text):
    if text is None: return ""
    return get_display(arabic_reshaper.reshape(str(text)))

class WelcomeWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(300)
        self.padding = dp(40)
        icon_box = BoxLayout(size_hint=(None, None), size=(dp(120), dp(120)))
        icon_box.pos_hint = {'center_x': 0.5}
        with icon_box.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.circle = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=self.update_circle, size=icon_box.size)
        name_lbl = Label(text="Fadi", font_size=sp(32), bold=True, color=(1,1,1,1))
        icon_box.add_widget(name_lbl)
        self.add_widget(icon_box)
        msg = Label(text=format_arabic("جاهز للبحث..."), font_size=sp(16), color=(0.4, 0.4, 0.4, 1))
        self.add_widget(msg)

    def update_circle(self, instance, value):
        self.circle.pos = instance.pos
        self.circle.size = instance.size

class ProfessionalCard(BoxLayout):
    def __init__(self, item_data, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(115)
        self.padding = [dp(15), dp(10), dp(15), dp(10)]
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # حماية ضد القيم الفارغة
        lbl_name = Label(text=format_arabic(item_data.get('name', '---')), color=(0.1, 0.15, 0.3, 1), font_size=sp(17), bold=True)
        self.add_widget(lbl_name)
        
        stats = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        stats.add_widget(Label(text=format_arabic(item_data.get('qty', '0')), color=(0.1, 0.6, 0.2, 1), bold=True))
        stats.add_widget(Label(text=format_arabic(item_data.get('unit', '-')), color=(0.3, 0.3, 0.3, 1)))
        stats.add_widget(Label(text=format_arabic(item_data.get('code', '-')), color=(0.3, 0.3, 0.3, 1)))
        self.add_widget(stats)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FadiInventoryApp(App):
    def build(self):
        self.searchable_data = [] # قائمة محلية ثابتة للبحث
        self.loading_complete = False
        
        main_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # الشريط العلوي
        header = BoxLayout(size_hint_y=None, height=dp(70))
        with header.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.rect = Rectangle()
        header.bind(pos=lambda i,p: setattr(self.rect, 'pos', p), size=lambda i,s: setattr(self.rect, 'size', s))
        header.add_widget(Label(text="INVENTORY SYSTEM", bold=True))
        main_box.add_widget(header)
        
        self.search_input = TextInput(hint_text=format_arabic('ابدأ الكتابة للبحث...'), size_hint_y=None, height=dp(55), disabled=True)
        self.search_input.bind(text=self.on_search_change)
        main_box.add_widget(self.search_input)
        
        self.info_label = Label(text=format_arabic("جاري تهيئة النظام..."), size_hint_y=None, height=dp(30))
        main_box.add_widget(self.info_label)
        
        self.scroll = ScrollView()
        self.data_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        self.scroll.add_widget(self.data_grid)
        main_box.add_widget(self.scroll)
        
        threading.Thread(target=self.load_data, daemon=True).start()
        return main_box

    def load_data(self):
        # تحميل البيانات في قائمة محلية مؤقتة
        temp_data = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True, min_row=2):
                temp_data.append({
                    'code': str(row[0] or '-'),
                    'name': str(row[1] or '-'),
                    'unit': str(row[5] or '-'),
                    'qty': str(row[6] or '0'),
                    'search': f"{row[0]} {row[1]}".lower()
                })
            self.searchable_data = temp_data # تعيين القائمة مرة واحدة فقط
            self.loading_complete = True
            Clock.schedule_once(self.on_load_finished)
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', f"Error: {e}"))

    @mainthread
    def on_load_finished(self, dt):
        self.search_input.disabled = False
        self.info_label.text = format_arabic("جاهز للبحث")
        self.data_grid.add_widget(WelcomeWidget())

    def on_search_change(self, instance, value):
        Clock.schedule_once(lambda dt: self.perform_search(value), 0.1)

    @mainthread
    def perform_search(self, query):
        try:
            self.data_grid.clear_widgets()
            if not query.strip():
                self.data_grid.add_widget(WelcomeWidget())
                return

            count = 0
            # البحث في القائمة الثابتة (لا يوجد تداخل خيوط هنا)
            for item in self.searchable_data:
                if query.lower() in item['search']:
                    self.data_grid.add_widget(ProfessionalCard(item, 'Roboto'))
                    count += 1
                    if count >= 30: break
            
            self.info_label.text = format_arabic(f"نتائج: {count}")
        except Exception as e:
            self.info_label.text = "خطأ في البحث!"

if __name__ == '__main__':
    FadiInventoryApp().run()
