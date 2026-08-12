import os
import openpyxl
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle

# تغيير لون خلفية التطبيق بالكامل إلى الرمادي الفاتح جداً (تصميم عصري)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# --- كلاس مخصص لتصميم الشريط العلوي (Header) ---
class HeaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = 10
        with self.canvas.before:
            Color(0.12, 0.35, 0.71, 1)  # لون أزرق احترافي
            self.rect = Rectangle()
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# --- كلاس مخصص لتصميم كل صف كـ "بطاقة" (Card) مستقلة بزوايا دائرية ---
class CardLayout(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 65
        self.padding = [15, 0, 15, 0]
        
        with self.canvas.before:
            Color(1, 1, 1, 1)  # خلفية بيضاء للبطاقة
            self.rect = RoundedRectangle(radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # النص داخل البطاقة (لون داكن لسهولة القراءة)
        lbl = Label(
            text=text,
            color=(0.15, 0.15, 0.15, 1),
            bold=True,
            font_size=16,
            halign='left',
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
        
        main_box = BoxLayout(orientation='vertical', spacing=10)
        
        # 1. إضافة الشريط العلوي
        header = HeaderLayout()
        header_title = Label(
            text="INVENTORY MANAGEMENT",
            color=(1, 1, 1, 1),
            bold=True,
            font_size=20
        )
        header.add_widget(header_title)
        main_box.add_widget(header)
        
        # 2. شريط الحالة
        self.info_label = Label(
            text="Loading Data...",
            size_hint_y=None, 
            height=30,
            color=(0.4, 0.4, 0.4, 1), # رمادي
            bold=True
        )
        main_box.add_widget(self.info_label)
        
        # 3. شبكة البيانات
        self.data_grid = GridLayout(cols=1, spacing=10, padding=[15, 5, 15, 15], size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_grid)
        main_box.add_widget(scroll)
        
        self.load_excel_data()
        
        return main_box

    def load_excel_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_file = os.path.join(current_dir, 'inventory.xlsx')
        
        if not os.path.exists(excel_file):
            self.info_label.text = "Error: inventory.xlsx is missing!"
            self.info_label.color = (0.9, 0.1, 0.1, 1)
            return
            
        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = workbook.active
            
            rows_loaded = 0
            for row in sheet.iter_rows(values_only=True):
                row_values = [str(cell) for cell in row if cell is not None]
                if row_values:
                    row_text = "  |  ".join(row_values)
                    # إضافة البطاقة الاحترافية
                    card = CardLayout(text=row_text)
                    self.data_grid.add_widget(card)
                    rows_loaded += 1
                    
            if rows_loaded > 0:
                self.info_label.text = f"Successfully loaded {rows_loaded} items"
                self.info_label.color = (0.1, 0.6, 0.1, 1) # أخضر
            else:
                self.info_label.text = "File is empty!"
                self.info_label.color = (0.9, 0.1, 0.1, 1)
                
        except Exception as e:
            self.info_label.text = f"Error: {str(e)[:40]}" 
            self.info_label.color = (0.9, 0.1, 0.1, 1)

if __name__ == '__main__':
    FadiInventoryApp().run()
