from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify, render_template
from flask import send_from_directory
from flask_cors import CORS
import mysql.connector
import bcrypt
from datetime import timedelta
import os
import hashlib
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from werkzeug.utils import secure_filename

#OTP LIB 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


app = Flask(__name__, static_folder='static', template_folder='templates')


#OTP auth
otp_store = {}
SMTP_EMAIL = "medtech.appointment@gmail.com"
SMTP_PASSWORD = "sbfqvehaedjpwbze"  # Use App Password for Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Enhanced CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Encryption Configuration
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'your-32-byte-encryption-key-here!!')[:32].encode()

class MessageEncryption:
    @staticmethod
    def encrypt_message(message, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext + encryptor.tag).decode('utf-8')

    @staticmethod
    def decrypt_message(encrypted_message, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        try:
            data = base64.b64decode(encrypted_message)
            iv, tag = data[:12], data[-16:]
            ciphertext = data[12:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return "[Decryption Failed]"

    @staticmethod
    def encrypt_file(file_data, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(file_data) + encryptor.finalize()
        return iv + ciphertext + encryptor.tag

    @staticmethod
    def decrypt_file(encrypted_data, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        try:
            iv = encrypted_data[:12]
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[12:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    @staticmethod
    def hash_sha256(text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12805028",
        password="dcGkiB2xte",
        database="sql12805028"
    )

# Improved login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "msg": "Email and password are required"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()

        if not user:
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"success": False, "msg": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"success": False, "msg": f"Login error: {str(e)}"}), 500
    
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "Missing JSON data"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "msg": "Email and password are required"}), 400

        # Check if user already exists
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            db.close()
            return jsonify({"success": False, "msg": "Email already registered"}), 409

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert the user into the database
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed_password))
        db.commit()
        db.close()

        return jsonify({"success": True, "msg": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "msg": f"Registration error: {str(e)}"}), 500

# Enhanced inbox endpoint with decryption
@app.route('/api/inbox', methods=['GET'])
@jwt_required()
def get_inbox_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key
            FROM messages 
            WHERE recipient_email = %s 
            ORDER BY timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        # Decrypt messages if they are encrypted
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
            
            if message['is_encrypted']:
                # Decrypt subject and body
                message['subject'] = MessageEncryption.decrypt_message(message['subject'])
                message['body'] = MessageEncryption.decrypt_message(message['body'])
                message['decrypted'] = True
            else:
                message['decrypted'] = False
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load inbox: {str(e)}"
        }), 500

# Enhanced sent messages endpoint with decryption
@app.route('/api/sent', methods=['GET'])
@jwt_required()
def get_sent_messages():
    try:
        user_email = get_jwt_identity()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key
            FROM messages 
            WHERE sender_email = %s 
            ORDER BY timestamp DESC
        """, (user_email,))
        
        messages = cursor.fetchall()
        db.close()
        
        # Decrypt messages if they are encrypted
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
            
            if message['is_encrypted']:
                # Decrypt subject and body
                message['subject'] = MessageEncryption.decrypt_message(message['subject'])
                message['body'] = MessageEncryption.decrypt_message(message['body'])
                message['decrypted'] = True
            else:
                message['decrypted'] = False
        
        return jsonify({
            "success": True,
            "messages": messages
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to load sent messages: {str(e)}"
        }), 500

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from werkzeug.utils import secure_filename
import os

@app.route('/api/send', methods=['POST'])
@jwt_required()
def send_message():
    try:
        user_email = get_jwt_identity()
        recipient_email = request.form.get('recipient_email')
        subject = request.form.get('subject')
        body = request.form.get('body')
        encrypt_message = request.form.get('encrypt_message', 'true').lower() == 'true'
        files = request.files.getlist('attachments')

        if not recipient_email or not subject or not body:
            return jsonify({"success": False, "msg": "Recipient, subject, and body are required"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT email FROM users WHERE email = %s", (recipient_email,))
        recipient = cursor.fetchone()
        if not recipient:
            db.close()
            return jsonify({"success": False, "msg": "Recipient not found"}), 404

        final_subject = subject
        final_body = body
        is_encrypted = 0
        encrypted_key = None

        if encrypt_message:
            final_subject = MessageEncryption.encrypt_message(subject)
            final_body = MessageEncryption.encrypt_message(body)
            is_encrypted = 1
            encrypted_key = MessageEncryption.hash_sha256(base64.b64encode(ENCRYPTION_KEY).decode())

        saved_filenames = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file_data = file.read()
                encrypted_data = MessageEncryption.encrypt_file(file_data)
                with open(filepath, 'wb') as f:
                    f.write(encrypted_data)
                saved_filenames.append(filename)

        first_attachment = saved_filenames[0] if saved_filenames else None

        cursor.execute("""
            INSERT INTO messages (
                sender_email, recipient_email, subject, body,
                is_encrypted, encrypted_key, attachment_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_email,
            recipient_email,
            final_subject,
            final_body,
            is_encrypted,
            encrypted_key,
            first_attachment
        ))

        db.commit()
        db.close()

        return jsonify({
            "success": True,
            "msg": "Message sent successfully",
            "encrypted": encrypt_message,
            "attachments": saved_filenames
        }), 200

    except Exception as e:
        return jsonify({"success": False, "msg": f"Failed to send message: {str(e)}"}), 500


# Add endpoint to get encryption status
@app.route('/api/encryption-status', methods=['GET'])
@jwt_required()
def get_encryption_status():
    try:
        return jsonify({
            "success": True,
            "encryption_available": True,
            "default_encrypt": True
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"Failed to get encryption status: {str(e)}"
        }), 500

# Add user validation endpoint
@app.route('/api/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    try:
        user_email = get_jwt_identity()
        return jsonify({
            "success": True,
            "email": user_email
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": "Invalid token"
        }), 401

@app.route('/api/request-otp', methods=['POST'])
@jwt_required()
def request_otp():
    email = get_jwt_identity()

    if not email:
        return jsonify({"success": False, "msg": "Email is required"}), 400

    otp_code = str(secrets.randbelow(1000000)).zfill(6)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    otp_store[email] = {"otp": otp_code, "expires_at": expires_at}

    # Send the OTP via email
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = email
        msg['Subject'] = "Your OTP Code"

        body = f"Your OTP code is: {otp_code}. It will expire in 5 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())
        server.quit()

        return jsonify({"success": True, "msg": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "msg": f"Failed to send OTP: {str(e)}"}), 500



# verify-otp validation endpoint
@app.route('/api/verify-otp', methods=['POST'])
@jwt_required()
def verify_otp():
    data = request.get_json()
    user_email = get_jwt_identity()
    otp_input = data.get('otp')

    if not otp_input:
        return jsonify({"success": False, "msg": "OTP is required"}), 400

    stored = otp_store.get(user_email)

    if not stored:
        return jsonify({"success": False, "msg": "No OTP requested"}), 400

    if datetime.utcnow() > stored['expires_at']:
        return jsonify({"success": False, "msg": "OTP expired"}), 400

    if stored['otp'] != otp_input:
        return jsonify({"success": False, "msg": "Invalid OTP"}), 401

    # OTP is valid, delete it
    del otp_store[user_email]

    return jsonify({"success": True, "msg": "OTP verified successfully"}), 200

@app.route('/view_message/<string:message_id>', methods=['GET'])
def message_page(message_id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        message_id = int(message_id)


        cursor.execute("""
            SELECT id, sender_email, recipient_email, subject, body, 
                   timestamp, is_encrypted, encrypted_key, attachment_path
            FROM messages 
            WHERE id = %s
        """, (message_id,))

        messages = cursor.fetchall()
        db.close()

        if not messages:
            return "Message not found", 404

        # Decrypt subject and body if encrypted
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()

            if message['is_encrypted']:
                message['subject'] = MessageEncryption.decrypt_message(message['subject'])
                message['body'] = MessageEncryption.decrypt_message(message['body'])
                message['decrypted'] = True
            else:
                message['decrypted'] = False

        # ✅ Optional debug output
        print("DEBUG message data:", messages[0])

        return render_template('viewmessage.html', messages=messages)

    except Exception as e:
        print(f"Error loading message: {e}")
        return "An error occurred while loading the message", 500

    
@app.route('/reply', methods=['POST'])
@jwt_required()
def reply_message():
    try:
        user_email = get_jwt_identity()
        recipient_email = request.form.get('recipient_email')
        reply_body = request.form.get('replyBody')
        file = request.files.get('replyFile')
        encrypt_message = request.form.get('encrypt_message', 'true').lower() == 'true'

        if not recipient_email or not reply_body:
            return jsonify({"success": False, "msg": "Recipient and reply body are required"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check if recipient exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (recipient_email,))
        recipient = cursor.fetchone()
        if not recipient:
            db.close()
            return jsonify({"success": False, "msg": "Recipient not found"}), 404

        final_body = reply_body
        is_encrypted = 0
        encrypted_key = None
        if encrypt_message:
            final_body = MessageEncryption.encrypt_message(reply_body)
            is_encrypted = 1
            encrypted_key = MessageEncryption.hash_sha256(base64.b64encode(ENCRYPTION_KEY).decode())

        # Handle file upload
        attachment_path = None
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            attachment_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(attachment_path)

        # Insert reply as a new message
        cursor.execute("""
            INSERT INTO messages (
                sender_email, recipient_email, subject, body,
                is_encrypted, encrypted_key, attachment_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_email,
            recipient_email,
            'RE: (reply)',  # You can fetch and prepend the original subject if needed
            final_body,
            is_encrypted,
            encrypted_key,
            filename if attachment_path else None
        ))

        db.commit()
        db.close()
        return jsonify({"success": True, "msg": "Reply sent successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "msg": f"Failed to send reply: {str(e)}"}), 500
    

  

# Frontend routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/inbox')
def inbox_page():
    return render_template('inbox.html')

@app.route('/compose')
def compose_page():
    return render_template('compose.html')

@app.route('/sent')
def sent_page():
    return render_template('sent.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# Add this to handle the initial load
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)