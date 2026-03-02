from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture console messages
        page.on("console", lambda msg: print(f"Browser Console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser Error: {err.message}"))

        print("Navigating to http://localhost:5173/")
        try:
            page.goto("http://localhost:5173/", wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # Take screenshot
            page.screenshot(path="screenshot.png")
            print("Screenshot saved to screenshot.png")
            
            # Also dump body HTML
            with open("body.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Body HTML saved to body.html")
            
        except Exception as e:
            print(f"Playwright error: {e}")
        
        browser.close()

if __name__ == "__main__":
    run()
