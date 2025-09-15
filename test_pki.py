#!/usr/bin/env python3
"""
Test script for the PKI Certificate Manager application.
This script tests the core functionality without requiring the web interface.
"""

import requests
import json
import time
import sys

def test_pki_functionality():
    """Test the PKI application functionality."""
    
    base_url = "http://localhost:5001"
    
    print("Testing PKI Certificate Manager...")
    print("=" * 40)
    
    # Test 1: Key Generation
    print("1. Testing key generation...")
    try:
        response = requests.post(f"{base_url}/generate_key", 
                               json={"key_size": 2048},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✓ Key generation successful")
                private_key = data['private_key']
                public_key = data['public_key']
            else:
                print(f"   ✗ Key generation failed: {data.get('error')}")
                return False
        else:
            print(f"   ✗ Key generation failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Key generation failed: {e}")
        return False
    
    # Test 2: CSR Generation
    print("2. Testing CSR generation...")
    try:
        csr_data = {
            "private_key": private_key,
            "country": "US",
            "state": "California",
            "locality": "San Francisco",
            "organization": "Test Organization",
            "organizational_unit": "IT Department",
            "common_name": "test.example.com",
            "dns_names": ["test.example.com", "www.test.example.com"]
        }
        
        response = requests.post(f"{base_url}/generate_csr", 
                               json=csr_data,
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✓ CSR generation successful")
                csr = data['csr']
            else:
                print(f"   ✗ CSR generation failed: {data.get('error')}")
                return False
        else:
            print(f"   ✗ CSR generation failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ CSR generation failed: {e}")
        return False
    
    # Test 3: Certificate Signing (using the generated root CA)
    print("3. Testing certificate signing...")
    try:
        # Read the generated root CA files
        with open("root_ca.key", "r") as f:
            root_key = f.read()
        with open("root_ca.crt", "r") as f:
            root_cert = f.read()
        
        sign_data = {
            "root_certificate": root_cert,
            "root_private_key": root_key,
            "csr": csr,
            "validity_days": 365,
            "dns_names": ["test.example.com", "www.test.example.com"]
        }
        
        response = requests.post(f"{base_url}/sign_certificate", 
                               json=sign_data,
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✓ Certificate signing successful")
                signed_cert = data['certificate']
            else:
                print(f"   ✗ Certificate signing failed: {data.get('error')}")
                return False
        else:
            print(f"   ✗ Certificate signing failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Certificate signing failed: {e}")
        return False
    except FileNotFoundError:
        print("   ✗ Root CA files not found. Run generate_root_ca.py first.")
        return False
    
    print("\nAll tests passed! ✓")
    print("The PKI application is working correctly.")
    return True

def main():
    """Main function to run the tests."""
    print("PKI Certificate Manager Test Suite")
    print("==================================")
    
    # Check if the application is running
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✓ Application is running on http://localhost:5001")
        else:
            print("✗ Application is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("✗ Application is not running. Please start it first with:")
        print("  python3 app.py")
        print("  (Note: The app runs on port 5001)")
        return False
    
    print()
    
    # Run the tests
    success = test_pki_functionality()
    
    if success:
        print("\nTest Summary: All functionality working correctly!")
        return 0
    else:
        print("\nTest Summary: Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
