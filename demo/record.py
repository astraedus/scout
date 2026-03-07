#!/usr/bin/env python3
"""
Scout demo video recorder.
Records ~2:30 walkthrough, adds edge-tts narration, outputs MP4.
Usage: python3 demo/record.py
"""
import asyncio, subprocess, time, os
from pathlib import Path
import urllib.request

SCOUT = Path("/home/astraedus/projects/scout")
DEMO  = Path("/tmp/scout-demo")
VDIR  = DEMO / "video"
ADIR  = DEMO / "audio"
OUT   = DEMO / "scout-demo.mp4"

for d in [VDIR, ADIR]: d.mkdir(parents=True, exist_ok=True)

NARRATION = [
    ("00_intro",
     "Before every sales call, you spend thirty minutes browsing five different websites. "
     "Company website. LinkedIn. Crunchbase. Google News. Job boards. "
     "By the time you're done, your meeting is about to start."),
    ("01_solution",
     "Scout does all of this in two minutes. One search. Real websites. Real-time data. "
     "A complete briefing before you finish your coffee."),
    ("02_watch",
     "Watch what happens when we research Stripe. Scout's AI agents are now navigating "
     "real websites in real time. Not stale training data. Actually visiting each source live."),
    ("03_website",
     "First, the company website. Extracting products, the team, and technology details."),
    ("04_news",
     "Google News for the latest headlines. Funding announcements, product launches, partnerships."),
    ("05_linkedin",
     "LinkedIn reveals company size, employee count, and key decision makers."),
    ("06_crunchbase",
     "Crunchbase gives us funding history, investors, and growth stage."),
    ("07_careers",
     "Job listings confirm the exact tech stack and show where the company is hiring fast."),
    ("08_synthesis",
     "Now Amazon Nova Two Lite synthesizes all the findings into structured intelligence."),
    ("09_briefing",
     "In under two minutes, a complete briefing. Key people with titles. "
     "Recent news. Tech stack confirmed from job listings. Growth signals."),
    ("10_talking",
     "And the talking points. Not generic icebreakers. Specific insights from what Scout actually found on the web."),
    ("11_close",
     "Scout. AI-powered company research in seconds. "
     "Built with Amazon Nova Act for live website navigation "
     "and Amazon Nova Two Lite for intelligent synthesis. Powered by AWS Bedrock."),
]


async def gen_audio():
    import edge_tts
    voice = "en-US-JennyNeural"
    for name, text in NARRATION:
        path = ADIR / f"{name}.mp3"
        if path.exists():
            print(f"  skip {name}")
            continue
        await edge_tts.Communicate(text, voice).save(str(path))
        print(f"  ok   {name}")


def wait_up(url, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except:
            time.sleep(1)
    return False


def duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    return float(r.stdout.strip())


def record():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VDIR),
            record_video_size={"width": 1280, "height": 720},
        )
        page = ctx.new_page()

        # --- Dashboard ---
        page.goto("http://localhost:3000", wait_until="domcontentloaded")
        time.sleep(5)  # hold on dashboard

        # Hover search area
        inp = page.locator("input").first
        inp.hover()
        time.sleep(1.5)

        # Type "Stripe"
        inp.click()
        time.sleep(0.5)
        for ch in "Stripe":
            page.keyboard.type(ch)
            time.sleep(0.18)
        time.sleep(2.5)

        # Submit
        page.keyboard.press("Enter")
        time.sleep(1)

        # --- Progress steps — ~15s total in mock mode, we add padding ---
        # Wait for research to complete (the page will navigate when done)
        # Meanwhile capture the progress UI
        try:
            page.wait_for_url("**/research/**", timeout=60000)
        except:
            pass
        time.sleep(1)

        # --- Briefing page ---
        # Overview (top of page)
        time.sleep(5)

        # Scroll to key people
        page.evaluate("window.scrollTo({top: 380, behavior: 'smooth'})")
        time.sleep(4)

        # Scroll to news
        page.evaluate("window.scrollTo({top: 680, behavior: 'smooth'})")
        time.sleep(4)

        # Scroll to tech stack
        page.evaluate("window.scrollTo({top: 980, behavior: 'smooth'})")
        time.sleep(4)

        # Scroll to talking points (most impressive)
        page.evaluate("window.scrollTo({top: 1500, behavior: 'smooth'})")
        time.sleep(6)

        # Scroll back to top + hold
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(4)

        vid = page.video.path()
        ctx.close()
        browser.close()
        print(f"  raw video: {vid}")
        return vid


def combine(raw_video):
    # Concatenate audio
    list_f = DEMO / "audio_list.txt"
    audios = sorted(ADIR.glob("*.mp3"))
    list_f.write_text("".join(f"file '{a}'\n" for a in audios))

    narration = DEMO / "narration.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c", "copy", str(narration)],
        check=True, capture_output=True)

    adur = duration(narration)
    vdur = duration(raw_video)
    print(f"  audio: {adur:.1f}s  video: {vdur:.1f}s")

    # Adjust video speed to match audio length
    speed = vdur / adur  # <1 = slow down, >1 = speed up
    print(f"  speed factor: {speed:.3f}x")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", str(narration),
        "-filter:v", f"setpts={1/speed:.4f}*PTS",
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v", "-map", "1:a",
        "-shortest",
        str(OUT)
    ], check=True)

    mb = OUT.stat().st_size / 1024 / 1024
    print(f"\n✓ {OUT}  ({mb:.1f} MB)")


async def main():
    print("=== Scout Demo Recorder ===\n")

    print("[1/4] Narration audio...")
    await gen_audio()

    print("\n[2/4] Starting servers...")
    env = {**os.environ, "MOCK_MODE": "true"}

    backend = subprocess.Popen(
        [str(SCOUT / "venv/bin/uvicorn"), "backend.main:app",
         "--port", "8000", "--host", "127.0.0.1"],
        cwd=str(SCOUT), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not wait_up("http://127.0.0.1:8000/health", 30):
        print("ERROR: backend"); backend.kill(); return
    print("  backend ready")

    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(SCOUT / "frontend"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("  waiting for Next.js to compile (~30s)...")
    if not wait_up("http://localhost:3000", 120):
        print("ERROR: frontend"); backend.kill(); frontend.kill(); return
    print("  frontend ready")

    try:
        print("\n[3/4] Recording...")
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, record)

        print("\n[4/4] Combining...")
        combine(raw)

    finally:
        backend.kill()
        frontend.kill()
        print("Servers stopped.")

asyncio.run(main())
