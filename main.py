from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)

def extract_link(url):
    driver = None
    try:
        # --- CHROME SETUP ---
        chrome_options = Options()
        chrome_options.add_argument('--headless') # Headless zaroori hai server ke liye
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Auto-Install Driver (Jo abhi successful hua tha)
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"🚀 Processing: {url}")
        driver.get(url)

        # 1. 'Verify' Button (Click To Continue)
        verify_btn = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "verify_btn"))
        )
        
        # Click Button
        driver.execute_script("arguments[0].click();", verify_btn)
        print("✅ Button Clicked")

        # 2. Wait for Timer (12 Seconds)
        time.sleep(12) 
        
        # 3. Get Final Link
        final_link = verify_btn.get_attribute("href")

        if "javascript" not in final_link:
            return {"status": "success", "original_url": url, "extracted_link": final_link}
        else:
            return {"status": "fail", "message": "Link did not update after timer"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if driver:
            driver.quit()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "usage": "/solve?url=YOUR_LINK"})

@app.route('/solve', methods=['GET'])
def solve():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"status": "error", "message": "URL parameter missing"}), 400
        
    result = extract_link(target_url)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
