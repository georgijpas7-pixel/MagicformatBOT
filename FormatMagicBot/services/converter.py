from io import BytesIO
from PIL import Image


async def convert_image(file_bytes, target_format, quality, ico_size):
    img = Image.open(BytesIO(file_bytes))
    output = BytesIO()

    # Конвертация в зависимости от формата
    if target_format == "ICO":
        img = img.convert("RGBA")
        img.thumbnail((ico_size, ico_size), Image.Resampling.LANCZOS)
        # Делаем квадрат
        size = max(img.size)
        square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - img.size[0]) // 2
        y = (size - img.size[1]) // 2
        square.paste(img, (x, y))
        img = square
        img.save(output, format="ICO", sizes=[(size, size)])

    elif target_format in ["JPG", "JPEG"]:
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()
                             [-1] if img.mode == "RGBA" else None)
            img = background
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=quality, optimize=True)

    elif target_format == "WEBP":
        if img.mode in ("RGBA", "LA"):
            img.save(output, format="WEBP", quality=quality, lossless=False)
        else:
            img = img.convert("RGB")
            img.save(output, format="WEBP", quality=quality)

    else:  # PNG, BMP
        img.save(output, format=target_format)

    output.seek(0)
    return output.getvalue()
