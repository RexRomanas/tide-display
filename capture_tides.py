import asyncio
from playwright.async_api import async_playwright
from PIL import Image

async def capture_and_process_tides():
    # --- STEP 1: CAPTURE THE DATA ---
    async with async_playwright() as p:
        # Open a hidden browser window
        browser = await p.chromium.launch(headless=True)
        
        # Lock viewport tightly to the XIAO 7.5" 800x480 resolution ratio
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # Navigate to the target page
        url = "https://www.tide-forecast.com/locations/Myrtle-Beach-South-Carolina/tides/latest"
        print(f"Loading {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Inject CSS to hide unwanted side elements for a cleaner E-ink view
        await page.add_style_tag(content="header, footer, nav, .ads { display: none !important; }")
        
        # 🎯 DYNAMIC SEARCH: Hunt for the main tide table section header
        # This looks for the text heading on the page containing "Tide Table"
        heading_locator = page.get_by_role("heading", name="Myrtle Beach Tide Table", exact=False)
        
        # Fallback to a broader heading if the location name text varies slightly
        if not await heading_locator.is_visible():
            heading_locator = page.get_by_role("heading", name="Tide Table", exact=False)

        temp_color_img = "temp_color.png"

        if await heading_locator.is_visible():
            print("Found the target text header! Locating surrounding container layout...")
            
            # Find the parent layout container box holding the charts below that heading
            target_element = heading_locator.locator("xpath=./ancestor::section[1]")
            if not await target_element.is_visible():
                # Alternative fallback to a generic section block if layout changes slightly
                target_element = heading_locator.locator("xpath=..")
            
            # Force the browser to scroll smoothly straight to this calculated element
            await target_element.scroll_into_view_if_needed()
            await page.wait_for_timeout(1500) # Wait for graph animations to stabilize
            
            # Snap the image using the element's live bounding dimensions
            await target_element.screenshot(path=temp_color_img)
            print("Successfully captured the live dynamic layout area!")
            
        else:
            print("Warning: Dynamic header not found. Falling back to default center screen crop.")
            # Safety fallback crop if the text itself vanishes entirely
            await page.screenshot(path=temp_color_img, clip={"x": 150, "y": 450, "width": 1140, "height": 700})
            
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
