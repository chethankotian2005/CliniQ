#!/usr/bin/env python
"""
Debug doctor login issues
"""

import requests
import os
import sys
import django
from bs4 import BeautifulSoup

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

def debug_doctor_login():
    """Debug doctor login step by step"""
    
    login_url = "http://127.0.0.1:8000/doctors/login/"
    
    print("Debugging Doctor Login Process")
    print("=" * 40)
    
    # Start a session
    session = requests.Session()
    
    try:
        # Step 1: Get login page
        print("Step 1: Getting login page...")
        response = session.get(login_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR: Cannot access login page")
            return
            
        # Step 2: Extract CSRF token
        print("Step 2: Extracting CSRF token...")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"CSRF token found: {csrf_token[:20]}...")
        else:
            csrf_token = session.cookies.get('csrftoken')
            print(f"CSRF from cookies: {csrf_token[:20] if csrf_token else 'None'}...")
            
        if not csrf_token:
            print("ERROR: No CSRF token found")
            return
            
        # Step 3: Prepare login data
        print("Step 3: Preparing login data...")
        login_data = {
            'username': 'dr.smith',
            'password': 'doctor123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'Referer': login_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Step 4: Submit login
        print("Step 4: Submitting login...")
        login_response = session.post(login_url, data=login_data, headers=headers, allow_redirects=False)
        print(f"Login response status: {login_response.status_code}")
        
        # Step 5: Analyze response
        print("Step 5: Analyzing response...")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            print(f"SUCCESS: Redirected to {redirect_url}")
            
            if 'dashboard' in redirect_url:
                print("LOGIN SUCCESSFUL: Redirected to dashboard")
            else:
                print(f"UNEXPECTED: Redirected to {redirect_url}")
                
        elif login_response.status_code == 200:
            # Check for error messages in the response
            response_text = login_response.text
            
            if 'Invalid username or password' in response_text:
                print("ERROR: Invalid credentials")
            elif 'not registered as a doctor' in response_text:
                print("ERROR: User not registered as doctor")
            elif 'error' in response_text.lower():
                print("ERROR: Some error in login")
                # Try to extract error message
                error_soup = BeautifulSoup(response_text, 'html.parser')
                error_div = error_soup.find('div', class_='alert-danger')
                if error_div:
                    print(f"Error message: {error_div.get_text().strip()}")
            else:
                print("UNCLEAR: Login page returned, no obvious error")
                
        else:
            print(f"ERROR: Unexpected status code {login_response.status_code}")
            
        # Step 6: Try to access dashboard directly
        print("Step 6: Testing dashboard access...")
        dashboard_url = "http://127.0.0.1:8000/doctors/dashboard/"
        dashboard_response = session.get(dashboard_url, allow_redirects=False)
        print(f"Dashboard access status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("SUCCESS: Can access dashboard")
        elif dashboard_response.status_code == 302:
            redirect = dashboard_response.headers.get('Location', '')
            print(f"REDIRECT: Dashboard redirects to {redirect}")
        else:
            print(f"ERROR: Cannot access dashboard")
            
    except Exception as e:
        print(f"ERROR: Exception occurred - {e}")

if __name__ == "__main__":
    debug_doctor_login()