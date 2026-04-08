from src.transcriber import parse_syllables
words = ["เล็ก", "เป็น", "เห็น", "อร่อย", "อย่างไร", "อ่าน", "ที่นั่น", "หิว"]
for w in words:
    print(f"{w} -> {parse_syllables(w)}")
