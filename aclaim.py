import requests
import itertools
import threading
import time
import sys
from queue import Queue

class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def load_list_from_file(prompt):
    while True:
        path = input(prompt).strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"{Color.GREEN}Loaded {len(lines)} entries from {path}{Color.RESET}")
            return lines
        except:
            print(f"{Color.RED}File not found. Try again.{Color.RESET}")

# -----------------------------

class ProxyRotator:
    def __init__(self, proxies):
        self.cycle = itertools.cycle(proxies)

    def get_proxy(self):
        proxy = next(self.cycle)
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }

# -----------------------------

def send_discord_message(webhook_url, message):
    """
    SAFE: This only sends a normal webhook message.
    """
    if not webhook_url:
        return

    try:
        requests.post(
            webhook_url,
            json={"content": message},
            timeout=10
        )
    except:
        print(f"{Color.RED}[WARN] Failed to send Discord message{Color.RESET}")

# -----------------------------

def check_username_available(username, signup_url, proxy=None):
    """
    ----------------------------------------
    REPLACE_WITH_YOUR_API
    ----------------------------------------
    """
    print(f"{Color.CYAN}[SAFE MOCK] Checking {username}...{Color.RESET}")
    return username.endswith("7")  # example mock behavior

# -----------------------------

def create_account(username, email, password, signup_url, proxy=None):
    """
    ----------------------------------------
    REPLACE_WITH_YOUR_API
    ----------------------------------------
    """
    print(f"{Color.CYAN}[SAFE MOCK] Creating account → {username}{Color.RESET}")
    return True  # pretend success

def worker(queue, emails, signup_url, password, rotator, webhook_url):
    while not queue.empty():

        username = queue.get()
        proxy = rotator.get_proxy()

        # Match username with an email
        email_line = emails.pop(0) if emails else None
        if not email_line:
            print(f"{Color.RED}[ERROR] Out of emails!{Color.RESET}")
            return

        email, email_pass = email_line.split(":", 1)

        # Step 1: Check availability
        try:
            available = check_username_available(username, signup_url, proxy)
        except:
            print(f"{Color.YELLOW}[WARN] Proxy failed, rotating...{Color.RESET}")
            proxy = rotator.get_proxy()
            queue.put(username)  # retry
            continue

        if not available:
            print(f"{Color.RED}[TAKEN] {username}{Color.RESET}")
            with open("failed.txt", "a") as f:
                f.write(username + "\n")
            queue.task_done()
            continue

        print(f"{Color.GREEN}[AVAILABLE] {username}{Color.RESET}")

        # Step 2: Create Account
        success = create_account(username, email, password, signup_url, proxy)

        if success:
            print(f"{Color.GREEN}[SUCCESS] {username} → {email}{Color.RESET}")
            with open("success.txt", "a") as f:
                f.write(f"{username}:{email}:{password}\n")
            send_discord_message(webhook_url, f"✔ Account Created: **{username}**")
        else:
            print(f"{Color.RED}[FAILED] Could not create account for {username}{Color.RESET}")
            with open("failed.txt", "a") as f:
                f.write(username + "\n")
            send_discord_message(webhook_url, f"✖ Failed: {username}")

        queue.task_done()

def main():
    print("=== aclaim.py made by username785849 ===")

    usernames = load_list_from_file("Enter username list .txt: ")
    emails = load_list_from_file("Enter email list .txt (email:pass): ")
    proxies = load_list_from_file("Enter proxy .txt (ip:port): ")

    webhook_url = input("Enter Discord Webhook URL (or press Enter to skip): ").strip()

    signup_url = input("Enter signup page URL (placeholder only): ").strip()

    # Password prompt
    while True:
        password = input("Enter password for accounts: ")
        confirm = input("Confirm password: ")
        if password == confirm:
            break
        print(f"{Color.RED}Passwords do not match.{Color.RESET}")

    # Multi-threading
    thread_count = int(input("How many threads? (Recommended: 3–10): "))

    proxy_rotator = ProxyRotator(proxies)

    # Create queue
    q = Queue()
    for u in usernames:
        q.put(u)

    print(f"{Color.GREEN}Starting threads...{Color.RESET}")

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(
            target=worker,
            args=(q, emails, signup_url, password, proxy_rotator, webhook_url)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"{Color.CYAN}\n=== Finished (aclaim.py) ==={Color.RESET}")


if __name__ == "__main__":
    main()
