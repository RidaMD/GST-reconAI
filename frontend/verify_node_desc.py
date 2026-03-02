from playwright.sync_api import sync_playwright

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to dashboard...")
        page.goto("http://localhost:5173/")
        page.wait_for_timeout(2000)
        page.click("text=Skip & Use Existing DB Data")
        page.wait_for_timeout(3000)
        
        # Click a node. Since it's a canvas, it's hard to target a specific node.
        # But we can try to search for an invoice and click it.
        invoice_id = "INV0001"
        print(f"Searching for {invoice_id}...")
        page.fill("input[placeholder='Search InvoiceID, GSTIN...']", invoice_id)
        page.wait_for_timeout(1000)
        
        # The handleSearch logic automatically selects and centers the node.
        # So the properties-panel should already be populated.
        
        print("Checking Node Details panel...")
        summary_text = page.locator(".node-summary-box p").text_content()
        print(f"Detected Summary: {summary_text}")
        
        page.screenshot(path="node_description_verify.png")
        browser.close()

if __name__ == "__main__":
    verify_ui()
