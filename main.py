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

# مكتبات اللغة العربية
import arabic_reshaper
from bidi.algorithm import get_display

Window.clearcolor = (0.95, 0.95, 0.95, 1)

class HeaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = 10
        with self.canvas.before:
            Color(0.12, 0.35, 0.71, 1)
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
        self.height = 65
        self.padding = [15, 0, 15, 0]
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # معالجة النص العربي لشبك الحروف وعكس الاتجاه
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        lbl = Label(
            text=bidi_text,
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=(0.15, 0.15, 0.15, 1),
            bold=True,
            font_size=16,
            halign='right', # محاذاة لليمين
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FadiInventoryApp(App):
    def build(self):
        self.title = "Inventory App"
        self.all_data = [] # لتخزين البيانات في الذاكرة لتسريع البحث
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')
        
        main_box = BoxLayout(orientation='vertical', spacing=10)
        
        # 1. الشريط العلوي
        header = HeaderLayout()
        header_title = Label(text="INVENTORY SYSTEM", color=(1, 1, 1, 1), bold=True, font_size=20)
        header.add_widget(header_title)
        main_box.add_widget(header)
        
        # 2. مربع البحث الذكي
        self.search_input = TextInput(
            hint_text='Search / بحث...',
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None,
            height=50,
            multiline=False,
            padding_y=[15, 15],
            padding_x=[15, 15]
        )
        # تشغيل البحث تلقائياً عند كتابة أي حرف
        self.search_input.bind(text=self.on_search_change)
        main_box.add_widget(self.search_input)
        
        # 3. شريط الحالة
        self.info_label = Label(
            text="App Opened. Preparing Data...",
            size_hint_y=None, height=30, color=(0.12, 0.35, 0.71, 1), font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto'
        )
        main_box.add_widget(self.info_label)
        
        # 4. شبكة البيانات
        self.data_grid = GridLayout(cols=1, spacing=10, padding=[15, 5, 15, 15], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_grid)
        main_box.add_widget(scroll)
        
        # جدولة قراءة الملف
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
            
        if not os.path.exists(self.font_path):
            print("Warning: font.ttf is missing, Arabic text may appear corrupted.")

        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = workbook.active
            
            # قراءة كل الإكسل وتخزينه في الذاكرة مرة واحدة فقط
            for row in sheet.iter_rows(values_only=True):
                row_values = [str(cell) for cell in row if cell is not None]
                if row_values:
                    self.all_data.append("  |  ".join(row_values))
                    
            self.update_ui("") # عرض المنتجات للمرة الأولى
                
        except Exception as e:
            self.info_label.text = f"Error: {str(e)[:40]}" 
            self.info_label.color = (0.9, 0.1, 0.1, 1)

    def on_search_change(self, instance, value):
        # استدعاء تحديث الواجهة عند كتابة أي حرف
        self.update_ui(value)

    def update_ui(self, search_text):
        self.data_grid.clear_widgets()
        # تفكيك نص البحث إلى كلمات منفصلة لتطبيق "البحث الذكي"
        search_terms = search_text.lower().split()
        
        displayed_count = 0
        for item in self.all_data:
            match = True
            item_lower = item.lower()
            
            # التحقق مما إذا كانت *جميع* الكلمات المدخلة موجودة في هذا الصف (مهما كان الترتيب)
            for term in search_terms:
                if term not in item_lower:
                    match = False
                    break
                    
            if match:
                # حد أمان لمنع انهيار الشاشة عند عرض أعداد ضخمة
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
