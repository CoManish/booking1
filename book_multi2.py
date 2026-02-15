from playwright.sync_api import sync_playwright
import threading
import time
from datetime import datetime, timedelta

# ================= CONFIG =================

# Direct seat booking page
direct_spot_url = "https://sports.mitwpu.edu.in/sports/fdbbe72e-ea45-4ccb-afc1-dfcab4b49c97/slots/89d0f036-28ff-48a5-a72b-41da8a542657/seats"

# Target release time (HH, MM, SS)
target_hour = 19
target_minute = 11
target_second = 0

# Multiple test accounts + spot numbers
AUTH_FILES = [
    ("auth/auth1.json", "4"),
    ("auth/auth2.json", "6"),
    ("auth/auth3.json", "5"),
]

# ================= WAIT UNTIL TARGET =================

def wait_until_target(hour, minute, second):
    target_time = datetime.now().replace(
        hour=hour, minute=minute, second=second, microsecond=0
    )

    # If already passed, schedule next day
    if datetime.now() > target_time:
        target_time += timedelta(days=1)

    print(f"⏳ Waiting until {target_time.strftime('%H:%M:%S')} ...")

    while True:
        now = datetime.now()
        diff = (target_time - now).total_seconds()

        if diff <= 0:
            break

        if diff > 1:
            time.sleep(0.5)
        else:
            time.sleep(0.001)

    print("🚀 Release time reached!")

# ================= SAFE CLICK FUNCTION =================

def safe_click(locator, label, retries=20):
    """
    Waits until element is visible + enabled, then clicks.
    Retries multiple times.
    """

    for attempt in range(retries):
        try:
            locator.wait_for(state="visible", timeout=2000)

            if locator.is_enabled():
                locator.click()
                print(f"✅ Clicked: {label}")
                return True
            else:
                print(f"⏳ {label} disabled... retrying")

        except Exception as e:
            print(f"⚠ Attempt {attempt+1} failed for {label}: {e}")

        time.sleep(0.15)

    print(f"❌ Failed clicking: {label}")
    return False

# ================= MAIN BOOKING FUNCTION =================

def book_slot(auth_file, spot_number):

    print("\n===================================")
    print(f"🚀 Account: {auth_file}")
    print(f"🎯 Spot: {spot_number}")
    print("===================================")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows"
            ]
        )

        # ✅ Login before time using saved auth session
        context = browser.new_context(storage_state=auth_file)
        page = context.new_page()

        print("✅ Opening seat page early (already logged in)...")
        page.goto(direct_spot_url, wait_until="domcontentloaded")

        # Ensure page loaded
        page.wait_for_selector("text=Choose Your Spot", timeout=8000)
        print("🟢 Ready BEFORE release time.")

        # ================= WAIT =================
        wait_until_target(target_hour, target_minute, target_second)

        # ================= REFRESH ON RELEASE =================
        print("🔄 Refreshing page exactly at release second...")
        page.reload(wait_until="domcontentloaded")

        # Small UI stabilization delay
        time.sleep(0.3)

        # ================= CLICK SPOT (FIXED) =================

        print(f"🎯 Clicking Spot {spot_number}...")

        # ✅ Correct fix: exact match prevents 1 matching 10/11/12
        spot_btn = page.get_by_role(
            "button",
            name=str(spot_number),
            exact=True
        )

        if not safe_click(spot_btn, f"Spot {spot_number}"):
            print("❌ Spot click failed, exiting.")
            browser.close()
            return

        # ================= ACCEPT TERMS =================

        print("✅ Accepting Terms & Conditions...")
        page.get_by_label("I agree to the Terms & Conditions").check()

        # ================= CONFIRM =================

        print("🚀 Clicking Confirm...")
        confirm_btn = page.locator("button:has-text('Confirm')").first

        if not safe_click(confirm_btn, "Confirm Button"):
            print("❌ Confirm click failed.")
            browser.close()
            return

        print(f"🎉 Booking Completed Successfully for {auth_file}")

        time.sleep(5)
        browser.close()

# ================= MULTI ACCOUNT RUNNER =================

def run_all_accounts():
    threads = []

    for auth_file, spot in AUTH_FILES:
        t = threading.Thread(target=book_slot, args=(auth_file, spot))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

# ================= START =================

if __name__ == "__main__":
    run_all_accounts()