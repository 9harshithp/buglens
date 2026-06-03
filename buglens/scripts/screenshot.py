"""Capture a screenshot of the running Streamlit app for the README / demo."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://127.0.0.1:8501/"


async def capture() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        # Wait for the hero heading to render.
        await page.wait_for_selector("h1", timeout=30_000)
        await page.wait_for_timeout(1500)
        out = OUT_DIR / "buglens_ui.png"
        await page.screenshot(path=str(out), full_page=True)
        print(f"Saved {out}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
