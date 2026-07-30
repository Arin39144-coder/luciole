"""Génère les icônes PNG Luciole (firefly / luciole)."""
import struct
import zlib
from pathlib import Path


def create_png(size: int, path: Path):
    """Crée un PNG simple avec un cercle doré sur fond transparent."""
    pixels = []
    cx, cy = size // 2, size // 2
    radius = size // 2 - 2

    for y in range(size):
        row = []
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= radius:
                # Dégradé doré
                t = dist / radius
                r = int(251 - t * 60)
                g = int(191 - t * 40)
                b = int(36 + t * 20)
                row.extend([r, g, b, 255])
            elif dist <= radius + 1:
                row.extend([245, 158, 11, 200])
            else:
                row.extend([0, 0, 0, 0])
        pixels.append(bytes([0] + row))

    raw = b"".join(pixels)
    compressed = zlib.compress(raw, 9)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")

    path.write_bytes(png)
    print(f"Created {path} ({size}x{size})")


if __name__ == "__main__":
    assets = Path(__file__).parent / "assets"
    assets.mkdir(exist_ok=True)
    for s in (16, 48, 128):
        create_png(s, assets / f"icon-{s}.png")
