"""Capture screenshot of the architecture HTML diagram."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"
HTML = Path(__file__).resolve().parent.parent / "interview_prep" / "architecture.html"
URL = f"file://{HTML}"


async def capture() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 1100},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(800)
        out = OUT_DIR / "buglens_architecture.png"
        await page.screenshot(path=str(out), full_page=True)
        print(f"Saved {out}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
