import asyncio
from playwright.async_api import async_playwright
from PIL import Image

async def capture_and_process_tides():
    # --- STEP 1: CAPTURE THE DATA ---
    async with async_playwright() as p:
        # Open a hidden browser window
        browser = await p.chromium.launch(headless=True)
        
        # Lock viewport tightly to the XIAO 7.5" 800x480 resolution ratio
        context = await browser.new_context(viewport={"width": 800, "height": 480})
        page = await context.new_page()
        
        # Navigate to the target page
        url = "https://www.tide-forecast.com/locations/Myrtle-Beach-South-Carolina/tides/latest"
        print(f"Loading {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Inject CSS to hide unwanted side elements for a cleaner E-ink view
        await page.add_style_tag(content="header, footer, nav, .ads { display: none !important; }")
        
        # Target the specific container holding the graphical charts and weather info
        # Note: If the website layout changes, you may need to update this selector
        chart_element = await page.query_selector("main")
        temp_color_img = "temp_color.png"
        
        if chart_element:
            # Take a cropped screenshot of just the data container
            await chart_element.screenshot(path=temp_color_img)
        else:
            # Fallback: take a screenshot of the whole page if the specific element isn't isolated
            await page.screenshot(path=temp_color_img)
            
        await browser.close()

    # --- STEP 2: OPTIMIZE FOR MONOCHROME EPAPER ---
    print("Processing image for 1-bit monochrome display...")
    with Image.open(temp_color_img) as img:
        # Resize explicitly to the hardware specifications
        img_resized = img.resize((800, 480), Image.Resampling.LANCZOS)
        
        # Convert to pure Black & White ('1') using Floyd-Steinberg dithering
        # This prevents text from washing out and makes graphs crisp
        bw_dithered = img_resized.convert("1")
        
        # Save the finalized image ready for display download
        final_output = "xiao_tides_800x480.png"
        bw_dithered.save(final_output)
        print(f"Success! Output optimized for ePaper saved as: {final_output}")

asyncio.run(capture_and_process_tides())
