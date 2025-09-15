# PKI Certificate Manager

A comprehensive Python-based Public Key Infrastructure (PKI) application with a modern web interface for generating, signing, and managing X.509 certificates.

## Features

- **Key Generation**: Generate RSA key pairs (2048 or 4096 bits)
- **CSR Generation**: Create Certificate Signing Requests with customizable subject fields
- **Certificate Signing**: Sign CSRs using a root certificate authority
- **Root CA Upload**: Upload existing root certificates and private keys
- **File Management**: Download generated keys, CSRs, and certificates
- **Modern UI**: Responsive Bootstrap-based interface with real-time feedback

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your web browser and navigate to `http://localhost:5001`

## Usage Guide

### 1. Key Generation

1. Navigate to the "Key Generation" tab
2. Select the desired key size (2048 or 4096 bits)
3. Click "Generate Key Pair"
4. The generated private and public keys will be displayed
5. Use the download buttons to save the keys to your system

### 2. CSR Generation

1. Navigate to the "CSR Generation" tab
2. Paste your private key in PEM format (or use the key from step 1)
3. Fill in the certificate subject information:
   - **Country (C)**: Two-letter country code (e.g., US)
   - **State/Province (ST)**: State or province name
   - **Locality (L)**: City or locality name
   - **Organization (O)**: Organization name
   - **Organizational Unit (OU)**: Department or unit name
   - **Common Name (CN)**: Domain name or hostname
   - **DNS Names**: Comma-separated list of domain names for Subject Alternative Names
4. Click "Generate CSR"
5. Download the generated CSR file

### 3. Certificate Signing

1. Navigate to the "Certificate Signing" tab
2. Provide the root certificate in PEM format
3. Provide the root private key in PEM format
4. Paste the CSR to be signed
5. Set the certificate validity period (in days)
6. Optionally add DNS names for Subject Alternative Names
7. Click "Sign Certificate"
8. Download the signed certificate

### 4. Upload Root CA

1. Navigate to the "Upload Root CA" tab
2. Select your root certificate file (.pem or .crt)
3. Select your root private key file (.pem or .key)
4. Click "Upload Root CA"
5. The application will automatically populate the certificate signing form

## File Formats

The application supports the following file formats:

- **Certificates**: `.pem`, `.crt`
- **Private Keys**: `.pem`, `.key`
- **CSRs**: `.pem`, `.csr`

All files should be in PEM format (base64-encoded with headers).

## Security Considerations

- **Private Key Security**: Never share your private keys. The application processes keys in memory and does not store them permanently.
- **Root CA Protection**: Keep your root certificate authority secure and limit access to the private key.
- **Certificate Validation**: Always verify the authenticity of certificates before trusting them.
- **Network Security**: The application runs on localhost by default. For production use, implement proper security measures.

## API Endpoints

The application provides the following REST API endpoints:

- `POST /generate_key`: Generate RSA key pair
- `POST /generate_csr`: Generate Certificate Signing Request
- `POST /sign_certificate`: Sign a CSR with root certificate
- `POST /upload_root`: Upload root certificate and private key
- `POST /download/<file_type>`: Download generated files

## Project Structure

```
pki-certificate-manager/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── js/
│       └── app.js        # Frontend JavaScript
└── uploads/              # Uploaded files directory (created automatically)
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` or stop the process using port 5001
2. **Permission errors**: Ensure you have write permissions in the project directory
3. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
4. **File upload issues**: Check that the uploaded files are in the correct PEM format

### Error Messages

- **"Invalid file type"**: Ensure uploaded files have the correct extensions (.pem, .crt, .key, .csr)
- **"No files selected"**: Make sure both certificate and private key files are selected for upload
- **"Error generating key pair"**: Check that the key size is valid (2048 or 4096)

## Development

To modify or extend the application:

1. **Backend**: Edit `app.py` to add new endpoints or modify existing functionality
2. **Frontend**: Modify `templates/index.html` for UI changes or `static/js/app.js` for JavaScript functionality
3. **Styling**: Add custom CSS in the `<style>` section of the HTML template

## License

This project is provided as-is for educational and development purposes. Use at your own risk in production environments.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.
