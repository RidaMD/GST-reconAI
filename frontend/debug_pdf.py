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
            page.wait_for_timeout(2000)
            
            # Click "Skip & Use Existing DB Data"
            page.click("text=Skip & Use Existing DB Data")
            page.wait_for_timeout(2000)
            
            # Click on Financial Risk Scorer tab
            page.click("text=Financial Risk Scorer")
            page.wait_for_timeout(2000)
            
            # Click the first view audit button to generate the report
            # The button has a class btn-icon
            page.locator(".btn-icon").first.click()
            print("Clicked Generate Audit...")
            
            # Wait for LangChain to finish or error out
            page.wait_for_timeout(5000)           
            
            # Now click Save PDF
            print("Clicking Save PDF...")
            page.click("text=Save PDF")
            page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"Playwright error: {e}")
        
        browser.close()

if __name__ == "__main__":
    run()
