# save_auth.py
from playwright.sync_api import sync_playwright

def save_login_state(auth_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://sports.mitwpu.edu.in/sports/fdbbe72e-ea45-4ccb-afc1-dfcab4b49c97/slots/89d0f036-28ff-48a5-a72b-41da8a542657/seats")

        input(f"Log in manually, then press Enter to save {auth_file}...")

        context.storage_state(path=auth_file)
        browser.close()

if __name__ == "__main__":
    save_login_state("auth/auth4.json")

# 1032222234@mitwpu.edu.in

# ved123kulkarni
# ___________
# 1032222174@mitwpu.edu.in
# M@n!sh_21
# ____________
# sodagar.parth@mitwpu.edu.in
# Parth2309@
# ____________
# 1032222183@mitwpu.edu.in
# Nailesh@4563

# ___________________________
# 1032221267@mitwpu.edu.in
#Utsav123