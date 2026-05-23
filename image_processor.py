from PIL import Image, ImageEnhance, ImageOps

def prepare_image(image_path, width=100, brightness=1.0, invert=False):
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise RuntimeError(f"Не удалось открыть изображение: {e}")

    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        background.paste(image, (0, 0), image)
        image = background.convert("RGB")

    image = image.convert("L")

    try:
        image = ImageOps.autocontrast(image, cutoff=1)
    except:
        pass

    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)

    if invert:
        image = ImageOps.invert(image)

    original_width, original_height = image.size
    aspect_ratio = original_height / float(original_width)
    height = max(1, int(aspect_ratio * width * 0.45))
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    return image, width