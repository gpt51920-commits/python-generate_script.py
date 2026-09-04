"""
=======================================================
  REELS / TIKTOK SCRIPT GENERATOR v1.0
  Генерує готові сценарії для коротких відео
  Використовує Claude API

  ЗАПУСК:
    python generate_script.py

  АБО з параметрами:
    python generate_script.py --topic "morning routine" --count 5 --niche fitness
=======================================================
"""

import argparse
import anthropic
from datetime import datetime
from pathlib import Path

# -------------------------------------------------------
# НАЛАШТУВАННЯ
# -------------------------------------------------------

API_KEY    = "YOUR_API_KEY_HERE"   # ← Вставте свій ключ з console.anthropic.com
OUTPUT_DIR = Path("scripts")
MODEL      = "claude-3-5-sonnet-20241022"

# Доступні ніші
NICHES = {
    "finance":   "personal finance, money, investing, budgeting, wealth",
    "fitness":   "workout, health, nutrition, motivation, body transformation",
    "mindset":   "psychology, habits, productivity, self-improvement, success",
    "marketing": "business, branding, social media growth, sales, entrepreneurship",
    "tech":      "AI tools, software, gadgets, automation, digital lifestyle",
    "general":   "general viral content, lifestyle, motivation, tips and tricks"
}

# -------------------------------------------------------
# ГЕНЕРАЦІЯ СЦЕНАРІЮ
# -------------------------------------------------------

def generate_script(client, topic: str, niche: str, style: str = "viral") -> str:
    """Генерує один повний сценарій для Reels/TikTok."""

    niche_context = NICHES.get(niche, NICHES["general"])

    system_prompt = """You are an expert viral short-form video scriptwriter.
You write scripts for TikTok, Instagram Reels, and YouTube Shorts.
Your scripts always have a powerful hook that stops the scroll in the first 3 seconds.

Format every script EXACTLY like this — no deviations:

HOOK (first 3 seconds — stop the scroll):
[one punchy sentence that creates curiosity or shock]

BODY (15-40 seconds — deliver value):
[3-5 short punchy sentences. One idea per line. No filler words.]

CTA (last 3 seconds — what to do next):
[one clear action: follow, save, comment, share]

CAPTION (for the post):
[2-3 sentences + 5 relevant hashtags]

VISUAL SUGGESTIONS:
[2-3 quick notes on what to show on screen]

Keep it punchy. Keep it real. No corporate language. Write like you're talking to a friend."""

    user_message = f"""Write a viral Reels/TikTok script about: "{topic}"

Niche: {niche} ({niche_context})
Style: {style}

Make the hook irresistible. The body should deliver ONE clear insight or tip.
The CTA should feel natural, not forced."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return message.content[0].text.strip()


def generate_batch(client, topic: str, niche: str, count: int) -> list:
    """Генерує кілька варіантів сценарію для однієї теми."""
    scripts = []
    styles  = ["viral", "educational", "storytelling", "controversial", "motivational"]

    for i in range(count):
        style = styles[i % len(styles)]
        print(f"  → Script {i+1}/{count} (style: {style})...")
        script = generate_script(client, topic, niche, style)
        scripts.append({"style": style, "content": script})

    return scripts


# -------------------------------------------------------
# ЗБЕРЕЖЕННЯ
# -------------------------------------------------------

def save_scripts(topic: str, niche: str, scripts: list):
    """Зберігає всі сценарії у .txt файл."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Безпечна назва файлу
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
    safe_topic = safe_topic.strip().replace(" ", "_")[:40]
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M")
    filename   = f"{safe_topic}_{niche}_{timestamp}.txt"
    path       = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"  REELS/TIKTOK SCRIPTS\n")
        f.write(f"  Topic: {topic}\n")
        f.write(f"  Niche: {niche}\n")
        f.write(f"  Scripts: {len(scripts)}\n")
        f.write(f"  Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}\n")
        f.write("="*60 + "\n")

        for i, item in enumerate(scripts, 1):
            f.write(f"\n{'─'*60}\n")
            f.write(f"  SCRIPT #{i}  —  Style: {item['style'].upper()}\n")
            f.write(f"{'─'*60}\n\n")
            f.write(item["content"])
            f.write("\n")

    print(f"\n  💾 Saved: {path}")
    return path


# -------------------------------------------------------
# ІНТЕРАКТИВНИЙ РЕЖИМ
# -------------------------------------------------------

def interactive_mode(client):
    """Режим коли параметри не передані — питає у користувача."""
    print("\n" + "="*60)
    print("  REELS / TIKTOK SCRIPT GENERATOR")
    print("="*60)

    # Тема
    topic = input("\n  Enter topic (e.g. 'morning routine', 'why you stay broke'): ").strip()
    if not topic:
        topic = "why most people fail at their goals"

    # Ніша
    print("\n  Available niches:")
    for key in NICHES:
        print(f"    {key}")
    niche = input("\n  Choose niche (or press Enter for 'general'): ").strip().lower()
    if niche not in NICHES:
        niche = "general"

    # Кількість
    count_str = input("\n  How many script variations? (1-5, default 3): ").strip()
    try:
        count = max(1, min(5, int(count_str)))
    except ValueError:
        count = 3

    return topic, niche, count


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Reels/TikTok Script Generator")
    parser.add_argument("--topic", type=str, help="Video topic")
    parser.add_argument("--niche", type=str, default="general",
                        choices=list(NICHES.keys()), help="Content niche")
    parser.add_argument("--count", type=int, default=3,
                        help="Number of script variations (1-5)")
    args = parser.parse_args()

    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: Set your API key in the API_KEY variable.")
        print("   Get it at: https://console.anthropic.com")
        return

    client = anthropic.Anthropic(api_key=API_KEY)

    # Якщо тема не передана — інтерактивний режим
    if not args.topic:
        topic, niche, count = interactive_mode(client)
    else:
        topic = args.topic
        niche = args.niche
        count = args.count

    print(f"\n  Generating {count} scripts for: '{topic}' [{niche}]\n")

    scripts = generate_batch(client, topic, niche, count)
    path    = save_scripts(topic, niche, scripts)

    # Показати перший сценарій в консолі
    print("\n" + "="*60)
    print("  PREVIEW — Script #1:")
    print("="*60)
    print(scripts[0]["content"])
    print(f"\n  All {len(scripts)} scripts saved to: {path}\n")


if __name__ == "__main__":
    main()
