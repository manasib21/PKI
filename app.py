from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography import x509
import os
import tempfile
import datetime
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pem', 'crt', 'key', 'csr'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_key', methods=['POST'])
def generate_key():
    try:
        data = request.get_json()
        key_size = int(data.get('key_size', 2048))
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return jsonify({
            'success': True,
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_csr', methods=['POST'])
def generate_csr():
    try:
        data = request.get_json()
        
        # Load private key
        private_key_data = data['private_key']
        private_key = load_pem_private_key(private_key_data.encode(), password=None)
        
        # Create CSR
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, data.get('country', 'US')),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, data.get('state', '')),
            x509.NameAttribute(NameOID.LOCALITY_NAME, data.get('locality', '')),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, data.get('organization', '')),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, data.get('organizational_unit', '')),
            x509.NameAttribute(NameOID.COMMON_NAME, data.get('common_name', '')),
        ])).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain) for domain in data.get('dns_names', [])
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Serialize CSR
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)
        
        return jsonify({
            'success': True,
            'csr': csr_pem.decode('utf-8')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/sign_certificate', methods=['POST'])
def sign_certificate():
    try:
        data = request.get_json()
        
        # Load root certificate and key
        root_cert_data = data['root_certificate']
        root_key_data = data['root_private_key']
        
        root_cert = x509.load_pem_x509_certificate(root_cert_data.encode())
        root_key = load_pem_private_key(root_key_data.encode(), password=None)
        
        # Load CSR
        csr_data = data['csr']
        csr = x509.load_pem_x509_csr(csr_data.encode())
        
        # Create certificate
        cert = x509.CertificateBuilder().subject_name(
            csr.subject
        ).issuer_name(
            root_cert.subject
        ).public_key(
            csr.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=int(data.get('validity_days', 365)))
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain) for domain in data.get('dns_names', [])
            ]),
            critical=False,
        ).sign(root_key, hashes.SHA256())
        
        # Serialize certificate
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        
        return jsonify({
            'success': True,
            'certificate': cert_pem.decode('utf-8')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload_root', methods=['POST'])
def upload_root():
    try:
        if 'root_certificate' not in request.files or 'root_private_key' not in request.files:
            return jsonify({'success': False, 'error': 'Both certificate and private key files are required'})
        
        cert_file = request.files['root_certificate']
        key_file = request.files['root_private_key']
        
        if cert_file.filename == '' or key_file.filename == '':
            return jsonify({'success': False, 'error': 'No files selected'})
        
        if cert_file and key_file and allowed_file(cert_file.filename) and allowed_file(key_file.filename):
            cert_filename = secure_filename(cert_file.filename)
            key_filename = secure_filename(key_file.filename)
            
            cert_path = os.path.join(UPLOAD_FOLDER, cert_filename)
            key_path = os.path.join(UPLOAD_FOLDER, key_filename)
            
            cert_file.save(cert_path)
            key_file.save(key_path)
            
            # Read and return the content
            with open(cert_path, 'r') as f:
                cert_content = f.read()
            with open(key_path, 'r') as f:
                key_content = f.read()
            
            return jsonify({
                'success': True,
                'certificate': cert_content,
                'private_key': key_content,
                'message': 'Root certificate and key uploaded successfully'
            })
        
        return jsonify({'success': False, 'error': 'Invalid file type'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<file_type>', methods=['POST'])
def download_file(file_type):
    try:
        data = request.get_json()
        content = data.get('content', '')
        filename = data.get('filename', f'{file_type}.pem')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
