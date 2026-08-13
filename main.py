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

# ألوان الهوية العامة للتطبيق (طابع محاسبي احترافي)
COLOR_PRIMARY = (0.09, 0.24, 0.48, 1)      # أزرق داكن
COLOR_PRIMARY_LIGHT = (0.13, 0.32, 0.60, 1)
COLOR_HEADER_BG = (0.09, 0.24, 0.48, 1)
COLOR_ROW_WHITE = (1, 1, 1, 1)
COLOR_ROW_ALT = (0.94, 0.96, 0.99, 1)
COLOR_BORDER = (0.85, 0.87, 0.90, 1)
COLOR_TEXT_DARK = (0.12, 0.15, 0.22, 1)
COLOR_TEXT_GRAY = (0.45, 0.47, 0.52, 1)
COLOR_GREEN = (0.13, 0.55, 0.27, 1)
COLOR_RED = (0.75, 0.15, 0.15, 1)


def format_arabic(text):
    if text is None:
        return ""
    return get_display(arabic_reshaper.reshape(str(text)))


class WelcomeWidget(BoxLayout):
    def __init__(self, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(280)
        self.padding = dp(40)
        self.spacing = dp(15)

        icon_box = BoxLayout(size_hint=(None, None), size=(dp(110), dp(110)))
        icon_box.pos_hint = {'center_x': 0.5}
        with icon_box.canvas.before:
            Color(*COLOR_PRIMARY)
            self.circle = Ellipse(pos=icon_box.pos, size=icon_box.size)
        # (تم إصلاح الخطأ هنا: الربط الآن بدالة صحيحة بدل قيمة ثابتة)
        icon_box.bind(pos=self.update_circle, size=self.update_circle)

        name_lbl = Label(text="Fadi", font_size=sp(30), bold=True,
                          color=(1, 1, 1, 1), halign='center', valign='middle')
        name_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        icon_box.add_widget(name_lbl)

        self.add_widget(icon_box)

        msg = Label(
            text=format_arabic("جاهز للبحث... اكتب أي جزء من الاسم أو الرمز"),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            font_size=sp(15),
            color=COLOR_TEXT_GRAY,
            halign='center'
        )
        msg.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(msg)

        hint = Label(
            text=format_arabic("مثال: اكتب IGBT ثم أضف 71 للتصفية أكثر (لا يشترط التتابع)"),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            font_size=sp(12),
            color=(0.6, 0.62, 0.68, 1),
            halign='center'
        )
        hint.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(hint)

    def update_circle(self, instance, value):
        self.circle.pos = instance.pos
        self.circle.size = instance.size


class TableHeader(BoxLayout):
    """رأس الجدول الثابت بأسلوب برامج المحاسبة"""
    def __init__(self, font_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(42)

        with self.canvas.before:
            Color(*COLOR_HEADER_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        def make_header_label(text, size_hint_x):
            lbl = Label(
                text=format_arabic(text),
                font_name=font_path if os.path.exists(font_path) else 'Roboto',
                color=(1, 1, 1, 1),
                font_size=sp(13),
                bold=True,
                halign='center',
                valign='middle',
                size_hint_x=size_hint_x
            )
            lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
            return lbl

        # ترتيب الأعمدة من اليمين لليسار بصريًا (اسم المادة على أقصى اليمين)
        self.add_widget(make_header_label("الرصيد", 0.22))
        self.add_widget(make_header_label("رمز المادة", 0.26))
        self.add_widget(make_header_label("اسم المادة", 0.52))

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class TableRow(BoxLayout):
    """صف بيانات بشكل جدول احترافي (اسم المادة | رمز المادة | الرصيد)"""
    def __init__(self, item_data, font_path, is_alt, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(6), 0, dp(6), 0]

        bg_color = COLOR_ROW_ALT if is_alt else COLOR_ROW_WHITE
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.border_rect = Rectangle(pos=self.pos, size=(self.size[0], dp(1)))
        self.bind(pos=self.update_bg, size=self.update_bg)

        # عمود الرصيد
        try:
            qty_val = float(item_data['qty'])
            qty_color = COLOR_RED if qty_val <= 0 else COLOR_GREEN
        except (ValueError, TypeError):
            qty_color = COLOR_TEXT_DARK

        qty_box = BoxLayout(orientation='vertical', size_hint_x=0.22)
        qty_lbl = Label(
            text=format_arabic(item_data['qty']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=qty_color, font_size=sp(15), bold=True,
            halign='center', valign='middle'
        )
        qty_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        unit_lbl = Label(
            text=format_arabic(item_data['unit']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=COLOR_TEXT_GRAY, font_size=sp(10),
            halign='center', valign='middle'
        )
        unit_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        qty_box.add_widget(qty_lbl)
        qty_box.add_widget(unit_lbl)
        self.add_widget(qty_box)

        # عمود رمز المادة
        code_lbl = Label(
            text=format_arabic(item_data['code']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=COLOR_TEXT_DARK, font_size=sp(13),
            halign='center', valign='middle',
            size_hint_x=0.26
        )
        code_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        self.add_widget(code_lbl)

        # عمود اسم المادة
        name_lbl = Label(
            text=format_arabic(item_data['name']),
            font_name=font_path if os.path.exists(font_path) else 'Roboto',
            color=COLOR_TEXT_DARK, font_size=sp(14), bold=True,
            halign='right', valign='middle',
            size_hint_x=0.52,
            shorten=False
        )
        name_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', (size[0] - dp(10), None)))
        self.add_widget(name_lbl)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0], self.pos[1])
        self.border_rect.size = (self.size[0], dp(1))


class FadiInventoryApp(App):
    def build(self):
        self.searchable_data = []
        self.loading_complete = False
        self._search_event = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font.ttf')

        main_box = BoxLayout(orientation='vertical', spacing=0)

        # الشريط العلوي
        header = BoxLayout(size_hint_y=None, height=dp(64), padding=dp(15))
        with header.canvas.before:
            Color(*COLOR_PRIMARY)
            self.header_rect = Rectangle()
        header.bind(pos=lambda i, p: setattr(self.header_rect, 'pos', p),
                    size=lambda i, s: setattr(self.header_rect, 'size', s))

        header_lbl = Label(
            text=format_arabic("نظام إدارة مخزون قطع الغيار"),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            bold=True,
            font_size=sp(17),
            color=(1, 1, 1, 1),
            halign='right',
            valign='middle'
        )
        header_lbl.bind(size=lambda inst, size: setattr(inst, 'text_size', size))
        header.add_widget(header_lbl)
        main_box.add_widget(header)

        # مربع البحث
        search_container = BoxLayout(size_hint_y=None, height=dp(64),
                                      padding=[dp(15), dp(8), dp(15), dp(8)])
        with search_container.canvas.before:
            Color(1, 1, 1, 1)
            self.search_bg = RoundedRectangle(radius=[dp(8)])
        search_container.bind(pos=self.update_search_bg, size=self.update_search_bg)

        self.search_input = TextInput(
            hint_text=format_arabic('ابحث بأجزاء الاسم أو الرمز (مثال: igbt 71)'),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            font_size=sp(15),
            multiline=False,
            padding=[dp(15), dp(14)],
            halign='right',
            background_normal='',
            background_active='',
            background_color=(1, 1, 1, 1),
            foreground_color=COLOR_TEXT_DARK,
            cursor_color=COLOR_PRIMARY,
            disabled=True
        )
        self.search_input.bind(text=self.on_search_change)
        search_container.add_widget(self.search_input)
        main_box.add_widget(search_container)

        # شريط الحالة
        self.info_label = Label(
            text=format_arabic("جاري تهيئة النظام وتحميل البيانات..."),
            font_name=self.font_path if os.path.exists(self.font_path) else 'Roboto',
            size_hint_y=None,
            height=dp(30),
            color=COLOR_TEXT_GRAY,
            font_size=sp(13)
        )
        main_box.add_widget(self.info_label)

        # رأس الجدول (يظهر فقط أثناء عرض النتائج)
        self.table_header_container = BoxLayout(size_hint_y=None, height=0)
        main_box.add_widget(self.table_header_container)

        # منطقة العرض القابلة للتمرير
        self.scroll = ScrollView(size_hint=(1, 1), bar_width=dp(6))
        self.data_grid = GridLayout(cols=1, spacing=dp(1), padding=[0, 0, 0, dp(10)],
                                     size_hint_y=None)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        self.scroll.add_widget(self.data_grid)
        main_box.add_widget(self.scroll)

        threading.Thread(target=self.load_data, daemon=True).start()
        return main_box

    def update_search_bg(self, instance, value):
        self.search_bg.pos = instance.pos
        self.search_bg.size = instance.size

    def load_data(self):
        temp_data = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.xlsx')
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            sheet = wb.active
            skipped = 0
            for row in sheet.iter_rows(values_only=True, min_row=2):
                try:
                    code = str(row[0]) if len(row) > 0 and row[0] is not None else '-'
                    name = str(row[1]) if len(row) > 1 and row[1] is not None else '-'
                    unit = str(row[5]) if len(row) > 5 and row[5] is not None else '-'
                    qty = str(row[6]) if len(row) > 6 and row[6] is not None else '0'

                    # دمج كافة محتويات الأعمدة المتوفرة في نص بحث شامل
                    all_row_text = " ".join(
                        [str(cell) for cell in row if cell is not None]
                    ).lower()

                    temp_data.append({
                        'code': code,
                        'name': name,
                        'unit': unit,
                        'qty': qty,
                        'search': all_row_text
                    })
                except Exception:
                    # صف فاسد لا يوقف تحميل باقي الملف
                    skipped += 1
                    continue

            self.searchable_data = temp_data
            self.loading_complete = True
            Clock.schedule_once(self.on_load_finished)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_info(f"خطأ في قراءة الملف: {e}", COLOR_RED))

    @mainthread
    def on_load_finished(self, dt):
        self.search_input.disabled = False
        self.info_label.text = format_arabic(f"جاهز للبحث — {len(self.searchable_data)} مادة محمّلة")
        self.info_label.color = COLOR_PRIMARY
        self.data_grid.clear_widgets()
        self.data_grid.add_widget(WelcomeWidget(self.font_path))

    @mainthread
    def update_info(self, text, color):
        self.info_label.text = format_arabic(text)
        self.info_label.color = color

    def on_search_change(self, instance, value):
        if not self.loading_complete:
            return
        # إلغاء أي بحث مجدول سابق لضمان عدم تراكم عمليات البحث أثناء الكتابة السريعة
        if self._search_event is not None:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self.perform_search(value), 0.2)

    @mainthread
    def perform_search(self, query):
        try:
            self.data_grid.clear_widgets()

            if not query or not query.strip():
                self.table_header_container.height = 0
                self.table_header_container.clear_widgets()
                self.info_label.text = format_arabic(
                    f"جاهز للبحث — {len(self.searchable_data)} مادة محمّلة"
                )
                self.info_label.color = COLOR_PRIMARY
                self.data_grid.add_widget(WelcomeWidget(self.font_path))
                return

            # بحث ذكي: كل كلمة/جزء مكتوب (مفصول بمسافة) يجب أن يكون موجودًا
            # في أي مكان بالسطر، دون اشتراط التتابع أو الترتيب
            search_terms = query.lower().split()
            count = 0

            self.table_header_container.clear_widgets()
            self.table_header_container.add_widget(TableHeader(self.font_path))
            self.table_header_container.height = dp(42)

            MAX_RESULTS = 40
            for item in self.searchable_data:
                if all(term in item['search'] for term in search_terms):
                    self.data_grid.add_widget(
                        TableRow(item, self.font_path, is_alt=(count % 2 == 1))
                    )
                    count += 1
                    if count >= MAX_RESULTS:
                        break

            if count == 0:
                self.table_header_container.height = 0
                self.table_header_container.clear_widgets()
                self.info_label.text = format_arabic("لا توجد نتائج مطابقة لبحثك")
                self.info_label.color = COLOR_RED
            else:
                suffix = f" (عرض أول {MAX_RESULTS})" if count >= MAX_RESULTS else ""
                self.info_label.text = format_arabic(f"تم العثور على {count} نتيجة{suffix}")
                self.info_label.color = COLOR_GREEN

        except Exception:
            self.table_header_container.height = 0
            self.table_header_container.clear_widgets()
            self.info_label.text = format_arabic("حدث خطأ أثناء البحث")
            self.info_label.color = COLOR_RED


if __name__ == '__main__':
    FadiInventoryApp().run()
