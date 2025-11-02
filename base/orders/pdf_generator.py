from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import qrcode
import os
from django.conf import settings


def register_fonts():
    """Регистрирует шрифты для поддержки кириллицы"""
    try:
        # Пытаемся найти системные шрифты
        font_paths = [
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:/Windows/Fonts/arial.ttf',  # Windows
            'C:/Windows/Fonts/calibri.ttf',  # Windows
        ]
        
        font_found = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                    pdfmetrics.registerFont(TTFont('CustomFont-Bold', font_path))
                    font_found = True
                    break
                except:
                    continue
        
        if not font_found:
            # Fallback к встроенным шрифтам
            pdfmetrics.registerFont(TTFont('CustomFont', 'Helvetica'))
            pdfmetrics.registerFont(TTFont('CustomFont-Bold', 'Helvetica-Bold'))
            
    except Exception as e:
        print(f"Ошибка регистрации шрифта: {e}")
        pdfmetrics.registerFont(TTFont('CustomFont', 'Helvetica'))
        pdfmetrics.registerFont(TTFont('CustomFont-Bold', 'Helvetica-Bold'))


def generate_qr_code_image(code, size=80):
    """Генерирует QR-код как изображение для PDF"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return ImageReader(buffer)


def create_receipt_pdf(order, pickup, items, is_courier=False):
    """Создает PDF-чек для заказа в простом текстовом формате"""
    # Регистрируем шрифты
    register_fonts()
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Настройки
    left_margin = 20
    line_height = 14
    current_y = height - 40
    
    def draw_text(text, x, y, font="CustomFont", size=10, align="left"):
        c.setFont(font, size)
        if align == "center":
            text_width = c.stringWidth(text, font, size)
            x = (width - text_width) / 2
        elif align == "right":
            text_width = c.stringWidth(text, font, size)
            x = width - text_width - 20
        c.drawString(x, y, text)
    
    def draw_line():
        nonlocal current_y
        c.line(left_margin, current_y, width - left_margin, current_y)
        current_y -= 5
    
    def new_line(text="", font="CustomFont", size=10, align="left", bold=False):
        nonlocal current_y
        current_y -= line_height
        if text:
            font_name = f"{font}-Bold" if bold else font
            draw_text(text, left_margin, current_y, font_name, size, align)
        return current_y
    
    # Заголовок
    draw_text("=" * 120, left_margin, current_y, "CustomFont", 8)
    current_y -= 25
    draw_text("ЧЕК ЗАКАЗА", left_margin, current_y, "CustomFont-Bold", 16, "center")
    current_y -= 20
    draw_text("=" * 120, left_margin, current_y, "CustomFont", 8)
    current_y -= 15
    
    # Информация о заказе
    new_line(f"Номер заказа: {order.order_number}", bold=True)
    new_line(f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
    new_line(f"Клиент: {order.customer_name or 'Не указано'}")
    if order.customer_phone:
        new_line(f"Телефон: {order.customer_phone}")
    
    current_y -= 10
    draw_line()
    current_y -= 10
    
    # Информация о доставке
    if is_courier:
        new_line("ТИП ДОСТАВКИ: КУРЬЕР", bold=True, size=12)
        if order.address:
            new_line(f"Адрес доставки: {order.address}")
    else:
        if pickup and pickup.pharmacy:
            new_line("ТИП ДОСТАВКИ: САМОВЫВОЗ", bold=True, size=12)
            new_line(f"Аптека: {pickup.pharmacy.name}", bold=True)
            if pickup.pharmacy.address:
                new_line(f"Адрес: {pickup.pharmacy.address}")
    
    current_y -= 20
    draw_line()
    current_y -= 10
    
    # QR-код и код получения
    if pickup:
        new_line("КОД ДЛЯ ПОЛУЧЕНИЯ", bold=True, size=12)
        current_y -= 10
        
        # QR-код
        qr_img = generate_qr_code_image(pickup.code, 80)
        c.drawImage(qr_img, left_margin, current_y - 80, width=80, height=80)
        
        # Код получения рядом с QR
        draw_text(f"Код: {pickup.code}", left_margin + 100, current_y - 20, "CustomFont-Bold", 16)
        draw_text("(покажите этот код при получении)", left_margin + 100, current_y - 40, "CustomFont", 8)
        
        current_y -= 100
        draw_line()
        current_y -= 10
    
    # Товары
    new_line("ТОВАРЫ", bold=True, size=12)
    current_y -= 30
    
    # Заголовок таблицы товаров
    draw_text("Название", left_margin, current_y, "CustomFont-Bold", 9)
    draw_text("Кол-во", left_margin + 200, current_y, "CustomFont-Bold", 9)
    draw_text("Цена", left_margin + 250, current_y, "CustomFont-Bold", 9)
    draw_text("Сумма", left_margin + 300, current_y, "CustomFont-Bold", 9)
    current_y -= 15
    
    # Линия под заголовком
    c.line(left_margin, current_y, width - left_margin, current_y)
    current_y -= 10
    
    total_amount = 0
    current_pharmacy = None
    
    for item in items:
        # Если курьерская доставка, группируем по аптекам
        if is_courier:
            pharmacy_name = item.pharmacy_medicine.pharmacy.name
            if current_pharmacy != pharmacy_name:
                if current_pharmacy is not None:
                    current_y -= 5
                    draw_line()
                    current_y -= 5
                new_line(f"--- {pharmacy_name} ---", bold=True, size=10)
                current_y -= 20
                current_pharmacy = pharmacy_name
        
        item_total = float(item.total_price())
        total_amount += item_total
        
        # Название товара
        item_name = item.pharmacy_medicine.medicine.name
        if len(item_name) > 25:
            item_name = item_name[:22] + "..."
        
        draw_text(item_name, left_margin, current_y, "CustomFont", 9)
        draw_text(str(item.quantity), left_margin + 200, current_y, "CustomFont", 9)
        draw_text(f"{item.price_at_purchase} Br", left_margin + 250, current_y, "CustomFont", 9)
        draw_text(f"{item_total:.2f} Br", left_margin + 300, current_y, "CustomFont", 9)
        current_y -= 12
    
    # Итоговая линия
    current_y -= 5
    c.line(left_margin, current_y, width - left_margin, current_y)
    current_y -= 20
    
    # Итого
    draw_text("ИТОГО:", left_margin + 250, current_y, "CustomFont-Bold", 12)
    draw_text(f"{total_amount:.2f} Br", left_margin + 300, current_y, "CustomFont-Bold", 12)
    current_y -= 20
    
    # Способ оплаты
    payment_method = "Наличными" if order.payment_method == "cash" else "Картой при получении"
    new_line(f"Способ оплаты: {payment_method}")
    
    current_y -= 20
    draw_line()
    current_y -= 10
    
    # Подвал
    new_line("Спасибо за покупку!", align="center", bold=True)
    new_line("Ветеринарный портал", align="center")
    
    # Сохраняем PDF
    c.save()
    buffer.seek(0)
    return buffer


def generate_receipts_for_order(order):
    """Генерирует чеки для заказа в зависимости от типа доставки"""
    receipts = []
    
    if order.delivery_type == order.DELIVERY_COURIER:
        # Для курьерской доставки - один чек с курьерским кодом
        courier_pickup = order.pickups.filter(pharmacy__isnull=True).first()
        if courier_pickup:
            all_items = order.items.select_related('pharmacy_medicine__medicine', 'pharmacy_medicine__pharmacy').all()
            pdf_buffer = create_receipt_pdf(order, courier_pickup, all_items, is_courier=True)
            receipts.append({
                'filename': f'receipt_courier_{order.id}.pdf',
                'buffer': pdf_buffer,
                'type': 'courier'
            })
    else:
        # Для самовывоза - отдельный чек для каждой аптеки
        pharmacies = set(item.pharmacy_medicine.pharmacy for item in order.items.all())
        
        for pharmacy in pharmacies:
            pickup = order.pickups.filter(pharmacy=pharmacy).first()
            if pickup:
                pharmacy_items = order.items.filter(pharmacy_medicine__pharmacy=pharmacy)
                pdf_buffer = create_receipt_pdf(order, pickup, pharmacy_items, is_courier=False)
                receipts.append({
                    'filename': f'receipt_{order.id}_{pharmacy.id}.pdf',
                    'buffer': pdf_buffer,
                    'type': 'pharmacy',
                    'pharmacy': pharmacy
                })
    
    return receipts
