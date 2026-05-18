import io
from PIL import Image, ImageDraw


def create_leaderboard_image(sorted_players):
    img = Image.new("RGB", (700, 600), (15, 15, 15))
    draw = ImageDraw.Draw(img)

    y = 20

    draw.text((200, y), "🏆 TOP 15 LEADERBOARD", fill=(255, 215, 0))
    y += 50

    for i, (user, data) in enumerate(sorted_players, start=1):
        text = f"{i}º {user.name} — {data['trofeus']} 🏆 | 🎖️ {data['medalhas']}"
        draw.text((20, y), text, fill=(255, 255, 255))
        y += 35

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
