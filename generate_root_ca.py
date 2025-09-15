#!/usr/bin/env python3
"""
Utility script to generate a sample Root Certificate Authority for testing the PKI application.
This script creates a self-signed root certificate that can be used to sign other certificates.
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

def generate_root_ca():
    """Generate a self-signed root certificate authority."""
    
    # Generate private key
    print("Generating root CA private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    
    # Create root certificate
    print("Creating root certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Root CA"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT Department"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Test Root CA"),
    ])
    
    # Create certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=3650)  # 10 years
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            content_commitment=False,
            data_encipherment=False,
            encipher_only=False,
            decipher_only=False
        ),
        critical=True,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
        critical=False,
    ).add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(private_key.public_key()),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Serialize to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    
    # Save files
    with open("root_ca.key", "wb") as f:
        f.write(private_pem)
    
    with open("root_ca.crt", "wb") as f:
        f.write(cert_pem)
    
    print("Root CA generated successfully!")
    print(f"Private key saved to: root_ca.key")
    print(f"Certificate saved to: root_ca.crt")
    print(f"Certificate subject: {cert.subject}")
    print(f"Valid from: {cert.not_valid_before}")
    print(f"Valid until: {cert.not_valid_after}")
    
    return private_pem.decode('utf-8'), cert_pem.decode('utf-8')

if __name__ == "__main__":
    generate_root_ca()

