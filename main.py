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
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

class WelcomeWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(300)  # ارتفاع ثابت يمنع انهيار الشعار أو اختفائه
        self.padding = dp(40)
        self.spacing = dp(20)
        
        icon_box = BoxLayout(size_hint=(None, None), size=(dp(120), dp(120)))
        icon_box.pos_hint = {'center_x': 0.5}
        with icon_box.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.circle = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=self.update_circle, size=icon_box.size)
        
        name_lbl = Label(text="Fadi", font_size=sp(32), bold=True, color=(1,1,1,1), halign='center', valign='middle')
        name_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        icon_box.add_widget(name_lbl)
        
        msg_lbl = Label(
            text=format_arabic("مرحباً بك يا فادي\nابدأ البحث عن موادك الآن"),
            font_size=sp(16), color=(0.4, 0.4, 0.4, 1),
            halign='center'
        )
        msg_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        
        self.add_widget(icon_box)
        self.add_widget(msg_lbl)

    def update_circle(self, instance, value):
        self.circle.pos = instance.pos
        self.circle.size = instance.size

class HeaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = dp(15)
        with self.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.rect = Rectangle()
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ProfessionalCard(BoxLayout):
    def __init__(self, item_data, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(115) 
        self.padding = [dp(15), dp(10), dp(15), dp(10)]
        self.spacing = dp(8)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        self.lbl_name = Label(
            text=format_arabic(item_data['name']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.1, 0.15, 0.3, 1), font_size=sp(17), bold=True,
            halign='right', valign='middle'
        )
        self.lbl_name.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(self.lbl_name)
        
        sep = BoxLayout(size_hint_y=None, height=dp(1))
        with sep.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.sep_rect = Rectangle()
        sep.bind(pos=self.update_sep, size=self.update_sep)
        self.add_widget(sep)
        
        stats_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        try:
            qty_val = float(item_data['qty'])
            qty_color = (0.8, 0.1, 0.1, 1) if qty_val <= 0 else (0.1, 0.6, 0.2, 1)
        except:
            qty_color = (0.1, 0.6, 0.2, 1)

        stats_box.add_widget(self.create_stat_box("العدد", item_data['qty'], font_path, qty_color, True))
        stats_box.add_widget(self.create_stat_box("الواحدة", item_data['unit'], font_path, (0.3, 0.3, 0.3, 1), False))
        stats_box.add_widget(self.create_stat_box("رقم المادة", item_data['code'], font_path, (0.3, 0.3, 0.3, 1), False))
        
        self.add_widget(stats_box)

    def create_stat_box(self, title, value, font_path, val_color, is_bold):
        box = BoxLayout(orientation='vertical')
        lbl_val = Label(text=format_arabic(value), font_name=font_path if os.path.exists(font_path) else 'Roboto', color=val_color, font_size=sp(15), bold=is_bold)
        lbl_title = Label(text=format_arabic(title), font_name=font_path if os.path.exists(font_path) else 'Roboto', color=(0.6, 0.6, 0.6, 1), font_size=sp(12))
        box.add_widget(lbl_val)
        box.add_widget(lbl_title)
        return box

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def update_sep(self, instance, *args):
        instance.sep_rect.pos = instance.pos
        instance.sep_rect.size = instance.size

class FadiInventoryApp(App):
    def build(self):
        self.title = "Inventory App"
        self.all_data = []
        self.data_loaded = False  # علم لمنع أي بحث قبل اكتمال التحميل
        self.search_event = None
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')
        
        main_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        header = HeaderLayout()
        header.add_widget(Label(text="INVENTORY SYSTEM", color=(1,1,1,1), bold=True, font_size=sp(20)))
        main_box.add_widget(header)
        
        self.search_input = TextInput(
            hint_text=format_arabic('ابحث عن اسم، رقم، أو تفاصيل المادة...'),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None, height=dp(55), font_size=sp(16), multiline=False,
            padding=[dp(15), dp(15)], halign='right',
            background_normal='', background_color=(1, 1, 1, 1),
            cursor_color=(0.1, 0.3, 0.6, 1),
            disabled=True  # معطل لحين انتهاء تحميل البيانات تماماً
        )
        self.search_input.bind(text=self.on_search_change)
        
        search_container = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(15), 0, dp(15), 0])
        search_container.add_widget(self.search_input)
        main_box.add_widget(search_container)
        
        self.info_label = Label(
            text=format_arabic("جارٍ تهيئة النظام وتحميل البيانات..."),
            size_hint_y=None, height=dp(30), color=(0.5, 0.5, 0.5, 1), 
            font_size=sp(14), font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto'
        )
        main_box.add_widget(self.info_label)
        
        self.data_grid = GridLayout(cols=1, spacing=dp(12), padding=[dp(15), dp(5), dp(15), dp(15)], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_grid)
        main_box.add_widget(scroll)
        
        Clock.schedule_once(self.start_loading_thread, 0.1)
        
        return main_box

    def start_loading_thread(self, dt):
        threading.Thread(target=self.load_excel_data, daemon=True).start()

    def get_safe_value(self, row, index, default="-"):
        try:
            if index < len(row) and row[index] is not None:
                val = str(row[index]).strip()
                if val != "":
                    return val
        except Exception:
            pass
        return default

    def load_excel_data(self):
        excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        if not os.path.exists(excel_file):
            self.update_ui_state("ملف inventory.xlsx مفقود!", (0.9, 0.1, 0.1, 1), enable_search=False)
            return
            
        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = workbook.active
            
            temp_data = []
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                if row_idx == 0: continue 
                
                code = self.get_safe_value(row, 0, "-")
                name = self.get_safe_value(row, 1, "بدون اسم")
                unit = self.get_safe_value(row, 5, "-")
                qty = self.get_safe_value(row, 6, "0")
                
                full_search_text = f"{code} {name} {unit} {qty}".lower()
                
                temp_data.append({
                    'code': code,
                    'name': name,
                    'unit': unit,
                    'qty': qty,
                    'search_text': full_search_text
                })
            
            self.all_data = temp_data
            self.data_loaded = True
            
            Clock.schedule_once(lambda dt: self.finalize_loading(), 0)
                
        except Exception as e:
            self.update_ui_state(f"حدث خطأ: {str(e)[:40]}", (0.9, 0.1, 0.1, 1), enable_search=False)

    @mainthread
    def finalize_loading(self):
        self.search_input.disabled = False
        self.update_info_label("جاهز للبحث...", (0.1, 0.3, 0.6, 1))
        self.data_grid.clear_widgets()
        self.data_grid.add_widget(WelcomeWidget())

    @mainthread
    def update_info_label(self, text, color):
        self.info_label.text = format_arabic(text)
        self.info_label.color = color

    @mainthread
    def update_ui_state(self, text, color, enable_search):
        self.info_label.text = format_arabic(text)
        self.info_label.color = color
        self.search_input.disabled = not enable_search

    def on_search_change(self, instance, value):
        if not self.data_loaded:
            return  
        if self.search_event:
            self.search_event.cancel()
        self.search_event = Clock.schedule_once(lambda dt: self.perform_search(value), 0.3)

    @mainthread
    def perform_search(self, search_text):
        self.data_grid.clear_widgets()
        
        if not search_text or search_text.strip() == "":
            self.update_info_label("جاهز للبحث...", (0.1, 0.3, 0.6, 1))
            self.data_grid.add_widget(WelcomeWidget())
            return
        
        search_terms = search_text.lower().split()
        displayed_count = 0
        for item in self.all_data:
            match = True
            for term in search_terms:
                if term not in item['search_text']:
                    match = False
                    break
            if match:
                if displayed_count >= 30: break  
                card = ProfessionalCard(item_data=item, font_path=self.font_path)
                self.data_grid.add_widget(card)
                displayed_count += 1
        
        if displayed_count == 0:
            self.update_info_label("لا توجد نتائج مطابقة!", (0.8, 0.1, 0.1, 1))
        else:
            self.update_info_label(f"تم العثور على {displayed_count} نتيجة", (0.1, 0.6, 0.2, 1))

if __name__ == '__main__':
    FadiInventoryApp().run()
