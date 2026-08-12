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
from kivy.metrics import dp, sp

import arabic_reshaper
from bidi.algorithm import get_display

# لون خلفية التطبيق (رمادي فاتح جداً لراحة العين)
Window.clearcolor = (0.95, 0.95, 0.97, 1)

def format_arabic(text):
    """دالة مساعدة لضبط أي نص عربي"""
    if text is None: return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

class HeaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = dp(15)
        with self.canvas.before:
            Color(0.1, 0.3, 0.6, 1) # أزرق احترافي غامق
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
        self.height = dp(115) # ارتفاع البطاقة
        self.padding = [dp(15), dp(10), dp(15), dp(10)]
        self.spacing = dp(8)
        
        # خلفية البطاقة
        with self.canvas.before:
            Color(1, 1, 1, 1) # أبيض
            self.rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # --- القسم العلوي: اسم المادة ---
        self.lbl_name = Label(
            text=format_arabic(item_data['name']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.1, 0.15, 0.3, 1), # لون كحلي أنيق
            font_size=sp(17),
            bold=True,
            halign='right',
            valign='middle'
        )
        self.lbl_name.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(self.lbl_name)
        
        # --- خط فاصل خفيف ---
        sep = BoxLayout(size_hint_y=None, height=dp(1))
        with sep.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.sep_rect = Rectangle()
        sep.bind(pos=self.update_sep, size=self.update_sep)
        self.add_widget(sep)
        
        # --- القسم السفلي: معلومات المادة (العدد، الواحدة، الرمز) ---
        stats_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # العدد (تلوين ذكي: أحمر إذا كان 0، أخضر إذا كان متوفر)
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
        
        # القيمة (الرقم أو النص)
        lbl_val = Label(
            text=format_arabic(value),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=val_color,
            font_size=sp(15),
            bold=is_bold
        )
        # العنوان (مثلاً: الواحدة)
        lbl_title = Label(
            text=format_arabic(title),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.6, 0.6, 0.6, 1),
            font_size=sp(12)
        )
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
        self.search_event = None # متغير للتحكم بتأخير البحث (لمنع التجميد)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')
        
        main_box = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # 1. الشريط العلوي
        header = HeaderLayout()
        header.add_widget(Label(text="INVENTORY SYSTEM", color=(1,1,1,1), bold=True, font_size=sp(20)))
        main_box.add_widget(header)
        
        # 2. مربع البحث الذكي 
        self.search_input = TextInput(
            hint_text=format_arabic('ابحث عن اسم، رقم، أو تفاصيل المادة...'),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None, height=dp(55), font_size=sp(16), multiline=False,
            padding=[dp(15), dp(15)], halign='right',
            background_normal='', background_color=(1, 1, 1, 1),
            cursor_color=(0.1, 0.3, 0.6, 1)
        )
        self.search_input.bind(text=self.on_search_change)
        
        search_container = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(15), 0, dp(15), 0])
        search_container.add_widget(self.search_input)
        main_box.add_widget(search_container)
        
        # 3. شريط الحالة
        self.info_label = Label(
            text=format_arabic("جاري تجهيز البيانات..."),
            size_hint_y=None, height=dp(30), color=(0.5, 0.5, 0.5, 1), 
            font_size=sp(14), font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto'
        )
        main_box.add_widget(self.info_label)
        
        # 4. شبكة البيانات
        self.data_grid = GridLayout(cols=1, spacing=dp(12), padding=[dp(15), dp(5), dp(15), dp(15)], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_grid)
        main_box.add_widget(scroll)
        
        Clock.schedule_once(self.load_excel_data, 0.5)
        
        return main_box

    def load_excel_data(self, dt):
        excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        if not os.path.exists(excel_file):
            self.info_label.text = format_arabic("خطأ: ملف inventory.xlsx مفقود!")
            self.info_label.color = (0.9, 0.1, 0.1, 1)
            return
            
        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = workbook.active
            
            # قراءة الإكسل وتصنيف الأعمدة
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                if row_idx == 0: continue # تخطي صف العناوين الأول
                
                # ترتيب الأعمدة بناءً على ملفك (0:الرمز, 1:الاسم, 5:الواحدة, 6:العدد)
                code = str(row[0]) if len(row) > 0 and row[0] is not None else "-"
                name = str(row[1]) if len(row) > 1 and row[1] is not None else "بدون اسم"
                unit = str(row[5]) if len(row) > 5 and row[5] is not None else "-"
                qty = str(row[6]) if len(row) > 6 and row[6] is not None else "0"
                
                # دمج كل النص للبحث الذكي السريع
                full_search_text = f"{code} {name} {unit} {qty}".lower()
                
                self.all_data.append({
                    'code': code,
                    'name': name,
                    'unit': unit,
                    'qty': qty,
                    'search_text': full_search_text
                })
                    
            self.update_ui("")
                
        except Exception as e:
            self.info_label.text = f"Error: {str(e)[:40]}" 
            self.info_label.color = (0.9, 0.1, 0.1, 1)

    def on_search_change(self, instance, value):
        # السر هنا: إلغاء البحث القديم وبدء بحث جديد بعد 0.4 ثانية من توقف المستخدم عن الكتابة
        if self.search_event:
            self.search_event.cancel()
        self.search_event = Clock.schedule_once(lambda dt: self.update_ui(value), 0.4)

    def update_ui(self, search_text):
        self.data_grid.clear_widgets()
        search_terms = search_text.lower().split()
        
        displayed_count = 0
        for item in self.all_data:
            match = True
            for term in search_terms:
                if term not in item['search_text']:
                    match = False
                    break
                    
            if match:
                if displayed_count >= 150: # حد أمان لعرض النتائج
                    break
                card = ProfessionalCard(item_data=item, font_path=self.font_path)
                self.data_grid.add_widget(card)
                displayed_count += 1
                
        self.info_label.text = format_arabic(f"تم العثور على {displayed_count} مادة")
        self.info_label.color = (0.1, 0.6, 0.2, 1)

if __name__ == '__main__':
    FadiInventoryApp().run()
