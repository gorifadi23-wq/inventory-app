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
    def __init__(self, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(300)
        self.padding = dp(40)
        self.spacing = dp(15)
        
        icon_box = BoxLayout(size_hint=(None, None), size=(dp(120), dp(120)))
        icon_box.pos_hint = {'center_x': 0.5}
        with icon_box.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.circle = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=self.update_circle, size=icon_box.size)
        
        name_lbl = Label(text="Fadi", font_size=sp(32), bold=True, color=(1,1,1,1), halign='center', valign='middle')
        name_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        icon_box.add_widget(name_lbl)
        
        self.add_widget(icon_box)
        
        msg = Label(
            text=format_arabic("جاهز للبحث... ابدأ كتابة الكلمات المفتاحية"),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            font_size=sp(16), 
            color=(0.4, 0.4, 0.4, 1),
            halign='center'
        )
        msg.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(msg)

    def update_circle(self, instance, value):
        self.circle.pos = instance.pos
        self.circle.size = instance.size

class ProfessionalCard(BoxLayout):
    def __init__(self, item_data, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [dp(15), dp(12), dp(15), dp(12)]
        self.spacing = dp(8)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # اسم المادة مع دعم الالتفاف التلقائي لمنع قص الكلمات الطويلة
        self.lbl_name = Label(
            text=format_arabic(item_data['name']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.1, 0.15, 0.3, 1), 
            font_size=sp(16), 
            bold=True,
            halign='right',
            valign='middle',
            size_hint_y=None
        )
        self.lbl_name.bind(texture_size=self.update_name_size)
        self.add_widget(self.lbl_name)
        
        # خط فاصل خفيف
        sep = BoxLayout(size_hint_y=None, height=dp(1))
        with sep.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.sep_rect = Rectangle()
        sep.bind(pos=lambda inst, p: setattr(inst.canvas.children[0], 'pos', p),
                 size=lambda inst, s: setattr(inst.canvas.children[0], 'size', s))
        self.add_widget(sep)
        
        # القسم السفلي (العدد، الواحدة، رقم المادة)
        stats_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38))
        
        try:
            qty_val = float(item_data['qty'])
            qty_color = (0.8, 0.1, 0.1, 1) if qty_val <= 0 else (0.1, 0.6, 0.2, 1)
        except:
            qty_color = (0.1, 0.6, 0.2, 1)

        stats_box.add_widget(self.create_stat_box("العدد", item_data['qty'], font_path, qty_color, True))
        stats_box.add_widget(self.create_stat_box("الواحدة", item_data['unit'], font_path, (0.3, 0.3, 0.3, 1), False))
        stats_box.add_widget(self.create_stat_box("رقم المادة", item_data['code'], font_path, (0.3, 0.3, 0.3, 1), False))
        
        self.add_widget(stats_box)
        self.height = dp(110)  # قيمة مبدئية

    def update_name_size(self, instance, size):
        # ضبط مساحة النص ليتوافق مع عرض الشاشة والالتفاف
        instance.text_size = (self.width - dp(30), None)
        instance.height = size[1]
        # حساب الطول الكلي للبطاقة ديناميكياً بناءً على طول اسم المادة
        self.height = instance.height + dp(1) + dp(38) + dp(24)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.lbl_name.text_size = (self.width - dp(30), None)

    def create_stat_box(self, title, value, font_path, val_color, is_bold):
        box = BoxLayout(orientation='vertical', spacing=dp(2))
        lbl_val = Label(
            text=format_arabic(value),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=val_color, font_size=sp(14), bold=is_bold,
            halign='center', valign='middle'
        )
        lbl_val.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        
        lbl_title = Label(
            text=format_arabic(title),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.6, 0.6, 0.6, 1), font_size=sp(11),
            halign='center', valign='middle'
        )
        lbl_title.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        
        box.add_widget(lbl_val)
        box.add_widget(lbl_title)
        return box

class FadiInventoryApp(App):
    def build(self):
        self.searchable_data = []
        self.loading_complete = False
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')
        
        main_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # الشريط العلوي
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(15))
        with header.canvas.before:
            Color(0.1, 0.3, 0.6, 1)
            self.rect = Rectangle()
        header.bind(pos=lambda i, p: setattr(self.rect, 'pos', p), size=lambda i, s: setattr(self.rect, 'size', s))
        
        header_lbl = Label(
            text="INVENTORY SYSTEM", 
            bold=True, 
            font_size=sp(18),
            color=(1, 1, 1, 1),
            halign='right',
            valign='middle'
        )
        header_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        header.add_widget(header_lbl)
        main_box.add_widget(header)
        
        # مربع البحث
        self.search_input = TextInput(
            hint_text=format_arabic('ابحث بأجزاء الاسم، الرقم، أو أي تفاصيل...'),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None, 
            height=dp(55),
            font_size=sp(15),
            multiline=False,
            padding=[dp(15), dp(15)],
            halign='right',
            background_normal='',
            background_color=(1, 1, 1, 1),
            cursor_color=(0.1, 0.3, 0.6, 1),
            disabled=True
        )
        self.search_input.bind(text=self.on_search_change)
        
        search_container = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(15), 0, dp(15), 0])
        search_container.add_widget(self.search_input)
        main_box.add_widget(search_container)
        
        # شريط الحالة
        self.info_label = Label(
            text=format_arabic("جاري تهيئة النظام وتحميل البيانات..."),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None, 
            height=dp(30), 
            color=(0.5, 0.5, 0.5, 1),
            font_size=sp(13)
        )
        main_box.add_widget(self.info_label)
        
        # منطقة العرض القابلة للتمرير
        self.scroll = ScrollView(size_hint=(1, 1))
        self.data_grid = GridLayout(cols=1, spacing=dp(12), padding=[dp(15), dp(5), dp(15), dp(15)], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        self.scroll.add_widget(self.data_grid)
        main_box.add_widget(self.scroll)
        
        threading.Thread(target=self.load_data, daemon=True).start()
        return main_box

    def load_data(self):
        temp_data = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True, min_row=2):
                code = str(row[0] or '-')
                name = str(row[1] or '-')
                unit = str(row[5] or '-')
                qty = str(row[6] or '0')
                
                # دمج كافة محتويات الأعمدة المتوفرة في نص بحث شامل لضمان البحث المتفرق في أي عمود
                all_row_text = " ".join([str(cell) for cell in row if cell is not None]).lower()
                
                temp_data.append({
                    'code': code,
                    'name': name,
                    'unit': unit,
                    'qty': qty,
                    'search': all_row_text
                })
            
            self.searchable_data = temp_data
            self.loading_complete = True
            Clock.schedule_once(self.on_load_finished)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_info(f"خطأ في قراءة الملف: {e}", (0.9, 0.1, 0.1, 1)))

    @mainthread
    def on_load_finished(self, dt):
        self.search_input.disabled = False
        self.info_label.text = format_arabic("جاهز للبحث...")
        self.info_label.color = (0.1, 0.3, 0.6, 1)
        self.data_grid.clear_widgets()
        self.data_grid.add_widget(WelcomeWidget(self.font_path))

    @mainthread
    def update_info(self, text, color):
        self.info_label.text = format_arabic(text)
        self.info_label.color = color

    def on_search_change(self, instance, value):
        if not self.loading_complete:
            return
        Clock.schedule_once(lambda dt: self.perform_search(value), 0.1)

    @mainthread
    def perform_search(self, query):
        try:
            self.data_grid.clear_widgets()
            
            if not query or not query.strip():
                self.info_label.text = format_arabic("جاهز للبحث...")
                self.info_label.color = (0.1, 0.3, 0.6, 1)
                self.data_grid.add_widget(WelcomeWidget(self.font_path))
                return

            search_terms = query.lower().split()
            count = 0
            
            for item in self.searchable_data:
                # التحقق من أن جميع الكلمات المكتوبة (حتى لو متقطعة) موجودة في السطر
                match = True
                for term in search_terms:
                    if term not in item['search']:
                        match = False
                        break
                
                if match:
                    self.data_grid.add_widget(ProfessionalCard(item, self.font_path))
                    count += 1
                    if count >= 30:  # حد أقصى للسرعة
                        break
            
            if count == 0:
                self.info_label.text = format_arabic("لا توجد نتائج مطابقة لبحثك!")
                self.info_label.color = (0.8, 0.1, 0.1, 1)
            else:
                self.info_label.text = format_arabic(f"تم العثور على {count} نتيجة")
                self.info_label.color = (0.1, 0.6, 0.2, 1)
                
        except Exception as e:
            self.info_label.text = format_arabic("حدث خطأ أثناء البحث")
            self.info_label.color = (0.9, 0.1, 0.1, 1)

if __name__ == '__main__':
    FadiInventoryApp().run()
