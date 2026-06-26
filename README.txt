PROJECT WORKFLOW SUMMARY:
1. Python Script (capture_tides.py) scrapes the Tide Forecast URL.
2. Pillow library scales it to 800x480 and converts it to pure Black & White.
3. GitHub Actions (.github/workflows/update_tides.yml) runs this on a Cron loop.
4. The generated image pushes to GitHub as a public URL link.
5. ESPHome firmware (xiao_epaper.yaml) on the XIAO panel downloads that URL over Wi-Fi.
