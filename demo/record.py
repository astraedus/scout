#!/usr/bin/env python3
"""
Scout demo video recorder v2.
Records ~3 min walkthrough with live Bedrock backend + semantic search.
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

# Live EC2 backend
API_URL = "http://100.24.122.229"

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
     "Let's research a company. Scout's backend is live on AWS, "
     "using Amazon Nova Two Lite through Bedrock to synthesize real web data."),
    ("03_progress",
     "Watch the progress. Scout is visiting the company website, scraping Google News, "
     "checking LinkedIn, Crunchbase, and job listings. All live, all in real time."),
    ("04_synthesis",
     "Now Amazon Nova Two Lite synthesizes all the findings. "
     "Not template fill. Actual reasoning over the extracted data."),
    ("05_briefing",
     "In under two minutes. A complete briefing. Executive summary. Key people with titles. "
     "Recent news. Tech stack confirmed from job listings."),
    ("06_talking",
     "And the talking points. Not generic icebreakers. "
     "Specific insights from what Scout actually found on the web."),
    ("07_search_intro",
     "But here's where it gets powerful. After every research job, "
     "Scout automatically generates embedding vectors using Amazon Nova Multimodal Embeddings. "
     "This enables semantic search across all your research."),
    ("08_search_demo",
     "Watch. We search for A.I. safety company. "
     "Scout doesn't do keyword matching. It understands meaning. "
     "Anthropic ranks highest because the embedding space captures semantic similarity."),
    ("09_search_demo2",
     "Now let's try payment processing fintech. "
     "Stripe jumps to the top. The embeddings understand what these companies actually do."),
    ("10_close",
     "Scout. AI-powered company research in seconds. "
     "Built with three Amazon Nova services. "
     "Nova Act for live website navigation. "
     "Nova Two Lite for intelligent synthesis. "
     "And Nova Multimodal Embeddings for semantic memory. "
     "All powered by AWS Bedrock."),
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

        # --- Dashboard with history ---
        page.goto("http://localhost:3000", wait_until="domcontentloaded")
        time.sleep(6)  # show dashboard + existing history

        # Type company name
        inp = page.locator("input").first
        inp.click()
        time.sleep(0.5)
        for ch in "Salesforce":
            page.keyboard.type(ch)
            time.sleep(0.15)
        time.sleep(1.5)

        # Submit research
        page.keyboard.press("Enter")
        time.sleep(2)

        # --- Progress tracking (real backend ~20-40s) ---
        # Wait for navigation to briefing page
        try:
            page.wait_for_url("**/research/**", timeout=90000)
        except:
            pass
        time.sleep(2)

        # --- Briefing page ---
        time.sleep(5)  # overview

        # Scroll through sections
        page.evaluate("window.scrollTo({top: 400, behavior: 'smooth'})")
        time.sleep(4)

        page.evaluate("window.scrollTo({top: 700, behavior: 'smooth'})")
        time.sleep(4)

        page.evaluate("window.scrollTo({top: 1000, behavior: 'smooth'})")
        time.sleep(4)

        # Talking points
        page.evaluate("window.scrollTo({top: 1500, behavior: 'smooth'})")
        time.sleep(6)

        # Back to top
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(3)

        # --- Navigate back to home for semantic search ---
        page.goto("http://localhost:3000", wait_until="domcontentloaded")
        time.sleep(4)

        # Scroll to semantic search section
        page.evaluate("document.querySelector('form')?.closest('div')?.nextElementSibling?.scrollIntoView({behavior: 'smooth'})")
        time.sleep(1)
        # Find the semantic search input (second input on page)
        search_inputs = page.locator("input[placeholder*='Search']")
        if search_inputs.count() > 0:
            search_input = search_inputs.first
        else:
            search_input = page.locator("input").nth(1)

        search_input.click()
        time.sleep(0.5)

        # Type semantic search query
        for ch in "AI safety company":
            page.keyboard.type(ch)
            time.sleep(0.12)
        time.sleep(1)

        # Submit search
        page.keyboard.press("Enter")
        time.sleep(4)  # show results

        # Clear and try another query
        search_input.click(click_count=3)
        time.sleep(0.3)
        for ch in "payment processing fintech":
            page.keyboard.type(ch)
            time.sleep(0.12)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(5)  # show results

        # Hold on final results
        time.sleep(3)

        vid = page.video.path()
        ctx.close()
        browser.close()
        print(f"  raw video: {vid}")
        return vid


def combine(raw_video):
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

    speed = vdur / adur
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
    print(f"\n  {OUT}  ({mb:.1f} MB)")


async def main():
    print("=== Scout Demo Recorder v2 (Live Bedrock + Semantic Search) ===\n")

    print("[1/3] Narration audio...")
    await gen_audio()

    print("\n[2/3] Starting frontend (backend is live on EC2)...")
    # Verify EC2 backend is up
    print(f"  checking {API_URL}/health ...")
    if not wait_up(f"{API_URL}/health", 10):
        print("ERROR: EC2 backend not reachable")
        return
    print("  backend OK")

    env = {**os.environ, "NEXT_PUBLIC_API_URL": API_URL}
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(SCOUT / "frontend"),
        env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("  waiting for Next.js to compile (~30s)...")
    if not wait_up("http://localhost:3000", 120):
        print("ERROR: frontend"); frontend.kill(); return
    print("  frontend ready")

    try:
        print("\n[3/3] Recording...")
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, record)

        print("\n[4/4] Combining...")
        combine(raw)

    finally:
        frontend.kill()
        print("Frontend stopped.")

asyncio.run(main())
