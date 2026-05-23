# Файл main.py
import text  # Импортируем файл с данными

def convert_pixels_to_ascii(prepared_image, width, gradient_type="Normal"):
    pixels = prepared_image.getdata()
    # Обращаемся к словарю через text.IMAGE_GRADIENTS
    chars = text.IMAGE_GRADIENTS.get(gradient_type, text.IMAGE_GRADIENTS["Normal"])
    num_chars = len(chars)
    ascii_str = ""
    for pixel_value in pixels:
        safe_pixel = max(0, min(int(pixel_value), 255))
        char_index = (safe_pixel * (num_chars - 1)) // 255
        ascii_str += chars[char_index]
    return "\n".join([ascii_str[i:i+width] for i in range(0, len(ascii_str), width)])

def generate_text_ascii(txt, scale=1):
    if not txt: return ""
    txt = txt.upper()
    raw_lines = ["", "", "", "", ""]
    for char in txt:
        # Обращаемся к словарю через text.ASCII_FONT
        glyph = text.ASCII_FONT.get(char, ["     "] * 5)
        for i in range(5):
            raw_lines[i] += glyph[i] + " "
    
    if scale <= 1: return "\n".join(raw_lines)
    
    scaled_lines = []
    for line in raw_lines:
        new_line = "".join([c * scale for c in line])
        for _ in range(scale):
            scaled_lines.append(new_line)
    return "\n".join(scaled_lines)