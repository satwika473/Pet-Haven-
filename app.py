import re
import uuid 
from flask import send_from_directory
from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for, session as flask_session
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import random
import os
from bcrypt import checkpw
from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory

from datetime import date

app = Flask(__name__)
app.secret_key = 'pethaven'

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'static/db/Petheaven.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.jinja_env.add_extension('jinja2.ext.do')
migrate = Migrate(app, db)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jasnavig9@gmail.com'
app.config['MAIL_PASSWORD'] = 'guze fwag qsff hppm'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@gmail.com'
mail = Mail(app)


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    # Add service provider specific fields
    service_type = db.Column(db.String(50))
    location = db.Column(db.String(255))
    hourly_rate = db.Column(db.Float)
    certifications = db.Column(db.Text)
    experience = db.Column(db.Integer)
    id_proof_path = db.Column(db.String(255), nullable=True)
    qualification_path = db.Column(db.String(255), nullable=True)
    certification_path = db.Column(db.String(255), nullable=True)

class Pet(db.Model):
    __tablename__ = 'pet'

    pet_id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(50), nullable=False)
    age_months = db.Column(db.Integer, nullable=False)
    health_records = db.Column(db.String(200))
    price = db.Column(db.Numeric, nullable=False)
    availability_status = db.Column(db.String(20))
    achivement = db.Column(db.String(200))
    image = db.Column(db.String(255))
    description = db.Column(db.String(200))

class Cart(db.Model):
    __tablename__ = 'cart'

    id =db.Column(db.Integer, primary_key=True)
    pet_id =db.Column(db.Integer, nullable=False)

class AdminCart(db.Model):
    __tablename__ = 'admin_cart'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, nullable=False)

class Sale(db.Model):
    __tablename__ = 'sales'

    sale_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)
    sale_price = db.Column(db.Numeric, nullable=False)
    payment_method = db.Column(db.String, nullable=False, default="Cash On Delivery")
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)

class Sale_detail(db.Model):
    __tablename__= 'sale_detail'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sale_id = db.Column(db.Integer, nullable=False)
    breed_name = db.Column(db.String(50), nullable=False) 
    price =	db.Column(db.Numeric, nullable=False)
    dog_id = db.Column(db.Integer, nullable=False)	

class Dog_sales(db.Model):
    __tablename__= 'Dog_sales'

    breed_id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(50), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False, default = 0)
    price = db.Column(db.Integer, nullable=False)	

events_list = []
# Registration model
def generate_dog_id():
    last_dog = Registration.query.order_by(Registration.id.desc()).first()
    if last_dog:
        last_number = int(last_dog.id.replace("Dog", ""))
        next_number = last_number + 1
    else:
        next_number = 101  # Start from 101
    return f"Dog{next_number}"

class Registration(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=generate_dog_id)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    competition_name = db.Column(db.String(100), nullable=False)
    dog_name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    achievements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Added status
    
    event = db.relationship('Event', backref='registrations')

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    
    competitions_registered = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(200), nullable=False)  # Store the image path
    def is_active(self):
        return self.date >= date.today()
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')

    customer = db.relationship('Customer', backref=db.backref('payments', lazy=True))

class CartEvent(db.Model):
    __tablename__ = 'cart_event'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String, db.ForeignKey('registration.id'), nullable=False)
    event_price = db.Column(db.Float, db.ForeignKey('event.price'), nullable=False)
    
    registration = db.relationship('Registration', backref='cart_items')
    event = db.relationship('Event', backref='cart_items')


    # Relationships
    
# Temporary OTP Store
otp_store = {}

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}


# Ensure uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Routes

# Serve uploaded files from the 'uploads' folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/show-users')
def display_users():
    show_users()
    return "User data has been printed in the console."


@app.route('/delete_submission/<int:index>', methods=['GET'])
def delete_submission(index):
    # Get the list of submissions from the session
    submissions = session.get('submissions', [])

    # Ensure the index is valid
    if 0 <= index < len(submissions):
        # Remove the submission from the list
        submissions.pop(index)

        # Update the session with the modified submissions list
        session['submissions'] = submissions

    # Redirect back to the admin dashboard
    return redirect(url_for('admin_dashboard'))

@app.before_request
def ensure_fresh_session():
    # Clear session if the request is the first one after starting the app
    if not session.get('initialized'):
        session.clear()
        session['initialized'] = True



@app.route('/')
def home():
    # If no active session, render the customer landing page by default
    if not session.get('role'):
        return render_template('landing_page.html', user_name=None)

    # Check if the user is logged in as a customer
    if session['role'] == 'customer':
        user_name = session.get('fullname', 'Guest')
        return render_template('landing_page.html', user_name=user_name)

    # Check if the user is logged in as a service provider
    if session['role'] == 'service-provider':
        return redirect(url_for('service_provider_landing'))

    # Fallback for unexpected roles
    session.clear()
    return render_template('landing_page.html', user_name=None)



   
@app.route('/service-provider-landing')
def service_provider_landing():
    if 'fullname' in session and session['role'] == 'service-provider':
        user_name = session['fullname']
        return render_template('service_provider_landing.html', user_name=user_name)
    else:
        flash('Please log in first')
        return redirect(url_for('login'))

@app.route('/service_provider')
def service_provider():
    return render_template('service_provider.html')

    
@app.route('/logout')
def logout():
    # Get the role of the user before clearing the session
    user_role = session.get('role')
    
    # Debug: Print session content before clearing
    print(f"Session before logout: {session}")
    
    # Clear the session to log out the user
    session.clear()

    # Debug: Print session content after clearing
    print(f"Session after logout: {session}")
    
    # Flash message for logout success
    flash('You have been logged out successfully.')

    # Redirect based on the role of the user
    if user_role == 'customer':
        return redirect(url_for('home'))  # Redirect customer to the landing page
    elif user_role == 'service-provider':
        return redirect(url_for('service_provider_landing'))  # Redirect service provider to their landing page
    else:
        return redirect(url_for('login'))  # If no role is found, redirect to login page

  
@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    submissions = session.get('submissions', [])
    index_submissions = session.get('index_submissions', [])
    return render_template('admin_dashboard.html', submissions=submissions, index_submissions=index_submissions)

@app.route('/admin_landing')
def admin_landing():
    return render_template('admin_landing.html')

@app.route('/submit_application', methods=['POST'])
def submit_application():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    service_requested = request.form.get('service_requested')

    # Handle file uploads
    id_proof = None
    qualification = None
    certification = None

    # Save files with unique filenames
    if 'id_proof' in request.files:
        file = request.files['id_proof']
        if file and allowed_file(file.filename):
            id_proof =save_file_default(file)

    if 'qualification' in request.files:
        file = request.files['qualification']
        if file and allowed_file(file.filename):
            qualification = save_file_default(file)
            


    if 'certification' in request.files:
        file = request.files['certification']
        if file and allowed_file(file.filename):
            certification = save_file_default(file)

    # Store the submission data in session
    submissions = session.get('submissions', [])
    submissions.append({
    "full_name": full_name,
    "email": email,
    "phone": phone,
    "service_requested": service_requested,
    "id_proof": id_proof,
    "qualification": qualification,
    "certification": certification,
    "experience": request.form.get("experience", "N/A")
})

    session['submissions'] = submissions  # Store updated submissions in session

    # Redirect to home page after submission
    return redirect(url_for('home'))



def save_file_default(file):
    """Save files to the default 'uploads/' folder."""
    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None




@app.route('/upload-documents')
def upload_documents():
    return render_template('upload_doc.html')

@app.route('/home')
def home_page():
    return render_template('landing_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('index.html')  # Render the register page for GET requests

    # Handle POST request logic for registration
    data = request.get_json()

    # Validate common fields
    required_fields = ['fullname', 'email', 'password', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if data['password'] != data.get('confirm_password', ''):
        return jsonify({"error": "Passwords do not match"}), 400

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return jsonify({"error": "Invalid email address. Please use a valid format like name@example.com."}), 400

    # Role-based handling
    role = data['role']
    new_user = None

    if role == 'service-provider':
        # Validate service provider fields
        service_fields = ['service_type', 'location', 'hourly_rate', 'certifications', 'experience']
        for field in service_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required for service providers"}), 400

        # Create a new service provider user
        new_user = User(
            fullname=data['fullname'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            service_type=data['service_type'],
            location=data['location'],
            hourly_rate=float(data['hourly_rate']),
            certifications=data['certifications'],
            experience=int(data['experience']),
            id_proof_path=data.get('id_proof_path'),
            qualification_path=data.get('qualification_path'),
            certification_path=data.get('certifications_path')
        )
    elif role == 'customer':
        # Create a new customer user
        new_user = User(
            fullname=data['fullname'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
    else:
        return jsonify({"error": "Invalid role"}), 400

    # Simulate OTP sending (replace with actual logic if needed)

    otp = "123456"  # Simulated OTP



    # Response
    response_data = {
    "fullname": data['fullname'],
    "email": data['email'],
    "role": data['role']
     }

    return jsonify({

        "message": "Registration successful. OTP sent to your registered contact.",

        "otp": otp,

        "data": response_data

    })


# Route to Send OTP for Registration
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data['email']
    session['temp_email'] = email

    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email already registered!'}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        msg = Message('Your PetCare OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your OTP for registration is: {otp}"
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'OTP sent to your email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'}), 500

# Route to Verify OTP and Register User
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = session.get('temp_email')
    entered_otp = data['otp']
    password = data['password']
    fullname = data['fullname']
    role=data['role']
    

    if not email or email not in otp_store:
        return jsonify({'status': 'error', 'message': 'No OTP sent for this email.'}), 400

    if otp_store[email] != entered_otp:
        return jsonify({'status': 'error', 'message': 'Invalid OTP.'}), 400

    try:
        #print("Hello world")
        #print(role)
        #print("Hello worls")
        if role=="customer":
            new_user = User(fullname=fullname, email=email, password=password,role=role)
           
        elif role=='service-provider':
       
            service_type=data['service_type']
            location=data['location']
            hourly_rate=float(data['hourly_rate'])
            certifications=data['certifications']
            experience=int(data['experience'])
            #print(service_type, location, hourly_rate,certifications,experience)
            new_user = User(fullname=fullname, email=email, password=password,role=role,service_type=service_type,location=location,hourly_rate=hourly_rate,certifications=certifications,experience=experience)
            
        db.session.add(new_user)
        db.session.commit()
        del otp_store[email]
        session.pop('temp_email', None)

        # Send Registration Success Email
        msg = Message('Registration Successful - PetCare', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Hello {fullname},\n\nYour registration with PetCare was successful. Welcome to our platform!\n\nThank you,\nPetCare Team"
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'Registration successful! A confirmation email has been sent.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Registration failed: {str(e)}'}), 500

# Admin Route to Approve Users
@app.route('/admin/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    try:
        msg = Message('Registration Approved - PetCare', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = f"Hello {user.fullname},\n\nYour registration with PetCare has been approved. You can now log in to access our services.\n\nThank you,\nPetCare Team"
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'User approved and notified via email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send approval email: {str(e)}'}), 500

# Admin Route to Deny Users
@app.route('/admin/deny-user/<int:user_id>', methods=['POST'])
def deny_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    try:
        msg = Message('Registration Denied - PetCare', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = f"Hello {user.fullname},\n\nWe regret to inform you that your registration with PetCare has been denied. If you believe this is an error, please contact our support team.\n\nThank you,\nPetCare Team"
        mail.send(msg)

        db.session.delete(user)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'User denied and notified via email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send denial email: {str(e)}'}), 500
    # Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        files = {
            "id-proof": request.files.get('id-proof'),
            "qualification": request.files.get('qualification'),
            "Certifications": request.files.get('Certifications'),
        }
         
        paths={}
        errors = []
        for field, file in files.items():
            if field != "Certifications" and not file:  # Mandatory fields check
                errors.append(f"{field.replace('-', ' ').title()} is required.")
                continue

            if file and allowed_file(file.filename):
                filename = f"{field}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                paths[f"{field.replace('-', '_')}_path"] = filepath
            elif file:
                errors.append(f"Invalid file format for {field.replace('-', ' ').title()}.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('upload_form'))
        
        email = session.get('temp_email')  # Ensure the email is stored in the session
        if not email:
            flash('Error: No email associated with the session.', 'error')
            return redirect(url_for('upload_form'))
        
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.id_proof_path = paths.get('id_proof_path')
            user.qualification_path = paths.get('qualification_path')
            user.certification_path = paths.get('certification_path')
            db.session.commit()
            flash('Documents uploaded successfully and saved to your profile!', 'success')
        else:
            flash('Error: User not found in the database.', 'error')
        
        return redirect(url_for('upload_form'))


# Other Routes (Login, Password Reset, etc.) remain unchanged

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')  # Render the login page for GET request

    # Handle the POST request (when login form is submitted)
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Email and password are required!'}), 400

    email = data['email'].strip().lower()
    password = data['password']
    role = data.get('role')

    user = User.query.filter_by(email=email, role=role).first()

    if user and user.password == password:
        # Store user information in session
        session['user_id'] = user.id
        session['fullname'] = user.fullname
        session['role'] = user.role

        # Redirect based on role after login
        if role == "customer":
            return jsonify({'status': 'success', 'redirect_url': '/'})  # Redirect to customer landing page
        elif role == "service-provider":
            return jsonify({'status': 'success', 'redirect_url': '/service-provider-landing'})  # Redirect to service provider landing page
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password!'}), 401


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    new_password = data['new_password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 400

    user.password = new_password
    db.session.commit()

    del otp_store[email]
    return jsonify({'status': 'success', 'message': 'Password reset successful!'})

# New email configuration for accept/reject notifications
app.config['NOTIF_MAIL_SERVER'] = 'smtp.example.com'  # Replace with your email server
app.config['NOTIF_MAIL_PORT'] = 587
app.config['NOTIF_MAIL_USE_TLS'] = True
app.config['NOTIF_MAIL_USERNAME'] = 'jasnavig100@gmail.com'  # Replace with notification email
app.config['NOTIF_MAIL_PASSWORD'] = 'ectf zfsn anxi nmox'          # Replace with notification email password

# Initialize a separate Mail instance
notif_mail = Mail()


@app.route('/send_notification_email', methods=['POST'])
def send_notification_email():
    data = request.json
    email = data['email']
    action = data['action']
    
    subject = "Application Status Notification"
    if action == "accept":
        body = f"Dear {data['full_name']},\n\nYour application for the service '{data['service_requested']}' has been accepted.\n\nThank you!"
    elif action == "reject":
        body = f"Dear {data['full_name']},\n\nWe regret to inform you that your application for the service '{data['service_requested']}' has been rejected.\n\nThank you!"

    try:
        msg = Message(subject, sender=app.config['NOTIF_MAIL_USERNAME'], recipients=[email])
        msg.body = body
        notif_mail.send(msg)
        return jsonify({"message": "Notification email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
    
    
    
# Query all users from the database
def show_users():
    with db.app.app_context():  # Create an application context
        users = User.query.all()
        if users:
            print("User Data in the Database:")
            for user in users:
                print(f"ID: {user.id}, Fullname: {user.fullname}, Email: {user.email}, Role: {user.role}")
                if user.role == 'service-provider':
                    print(f"Service Type: {user.service_type}, Location: {user.location}, Hourly Rate: {user.hourly_rate}, Certifications: {user.certifications}, Experience: {user.experience}, IdProof: {user.id_proof_path}, Qualifiaction: {user.qualification_path}, CertificationPath: {user.certification_path}")
        else:
            print("No user data found in the database.")

# Function to handle filtering logic
def build_filter_query(breed, price, age):
    query =db.session.query(Pet)

    if breed and breed.strip():
        query = query.filter(Pet.breed == breed.strip())

    if price:
        if price == "low":
            query = query.filter(Pet.price < 6000)
        elif price == "medium":
            query = query.filter(Pet.price.between(6000, 10000))
        elif price == "high":
            query = query.filter(Pet.price.between(10000, 15000))
        elif price == "very_high":
            query = query.filter(Pet.price > 15000)

    if age:
        if age == "Puppy":
            query = query.filter(Pet.age_months <= 12)
        elif age == "Young":
            query = query.filter(Pet.age_months > 12, Pet.age_months <= 36)
        elif age == "Adult":
            query = query.filter(Pet.age_months > 36)

    return query


@app.route('/cannine_home', methods=['GET'])
def cannine_home():
    role = request.args.get('role', default='customer')
    breed_filter = request.args.get('breed')
    price_filter = request.args.get('price')
    age_filter = request.args.get('age')

    dogs_query = build_filter_query(breed_filter, price_filter, age_filter)
    dogs = dogs_query.all()

    for dog in dogs:
        dog.description = f"A {dog.breed} ({dog.age_months} months old) with health status: '{dog.health_records or 'No records'}' and achievements: '{dog.achivement or 'None'}'."
    
    return render_template("index_cannine.html", dogs=dogs, role=role)
        

def get_cart_data():
    cart_items = db.session.query(Cart).all()
    cart_details = []
    for item in cart_items:
        pet = db.session.query(Pet).filter_by(pet_id=item.pet_id).first()
        if pet:
            cart_details.append({
                'id': item.id,
                'pet_id': pet.pet_id,
                'name': pet.breed,
                'price': float(pet.price),
                'total': float(pet.price) ,
                'image': pet.image
            })

    subtotal = sum(item['total'] for item in cart_details)
    shipping = 500 if subtotal > 0 else 0
    gst = subtotal * 0.05
    sgst = subtotal * 0.05
    total = subtotal + shipping + gst + sgst

    return {
        'cart_details': cart_details,
        'subtotal': subtotal,
        'shipping': shipping,
        'gst': gst,
        'sgst': sgst,
        'total': total
    }

# Customer Cart Routes
@app.route('/cart', methods=['GET'])
def view_cart():
    cart_data = get_cart_data()
    return render_template(
        'cart.html',
        cart_items=cart_data['cart_details'],
        subtotal=cart_data['subtotal'],
        shipping=cart_data['shipping'],
        gst=cart_data['gst'],
        sgst=cart_data['sgst'],
        total=cart_data['total'],
        role='customer'
    )


@app.route('/add_to_cart/<int:pet_id>', methods=['POST'])
def add_to_cart(pet_id):
    try:
        pet =db.session.query(Pet).filter_by(pet_id=pet_id).first()
        if not pet:
            return "Pet not found", 404

        if pet.availability_status == 'sold':
            flash(f"{pet.breed} is no longer available for purchase.", "warning")
            return redirect(url_for('cannine_home'))

        cart_item =db.session.query(Cart).filter_by(pet_id=pet_id).first()
        if cart_item:
            flash(f"{pet.breed} is already in your cart!", "info")
            return redirect(url_for('cannine_home'))
        
        # Add new item to cart
        new_cart_item = Cart(pet_id=pet_id)
        db.session.add(new_cart_item)
        db.session.commit()
       
        flash(f"{pet.breed} has been added to your cart!", "success")
        return redirect(url_for('view_cart'))

    except Exception as e:
        print(f"Error adding to customer cart: {e}")
        return "Error adding item to cart", 500
    
@app.route('/delete_from_cart/<int:cart_item_id>', methods=['POST'])
def delete_from_cart(cart_item_id):
    cart_item = db.session.query(Cart).filter_by(id=cart_item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('view_cart'))
    
@app.route('/policy', methods=['GET'])
def policy():
    return render_template("policy.html")

@app.route('/admin', methods=['GET'])
def admin():
    role = request.args.get('role', default='admin')
    breed_filter = request.args.get('breed')
    price_filter = request.args.get('price')
    age_filter = request.args.get('age')

    dogs_query = build_filter_query(breed_filter, price_filter, age_filter)
    dogs = dogs_query.all()

    for dog in dogs:
        dog.description = f"A {dog.breed} ({dog.age_months} months old) with health status: '{dog.health_records or 'No records'}' and achievements: '{dog.achivement or 'None'}'."
    
    return render_template("admin.html", dogs=dogs, breed=breed_filter, price=price_filter, age=age_filter)

@app.route('/edit_dog/<int:pet_id>', methods=['POST', 'GET'])
def edit_dog(pet_id):
    pet = db.session.query(Pet).filter_by(pet_id=pet_id).first()
    if not pet:
        flash("Pet not found", "error")
        return redirect(url_for('admin'))

    if request.method == 'POST':
        changes_made = False
        fields = {
            'breed': request.form.get('breed', pet.breed),
            'price': float(request.form.get('price', pet.price)),
            'age_months': int(request.form.get('age', pet.age_months)),
            'health_records': request.form.get('Health_Record', pet.health_records),
            'availability_status': request.form.get('Availability', pet.availability_status),
            'description': request.form.get('description', pet.description),
            'achivement': request.form.get('achivement', pet.achivement),
        }

        # Check and apply changes
        for field, value in fields.items():
            if getattr(pet, field) != value:
                setattr(pet, field, value)
                changes_made = True

        if changes_made:
            try:
                db.session.commit()
                flash(f"Details for {pet.breed} updated successfully!", "success")
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error in editing {pet.breed}", "error")

    return render_template('edit_dog.html',pet=pet)

@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        try:
            image = request.files['image']

            UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

            if not image:
                flash("Error in adding image", "error")
                return redirect(request.url)

                
            if image:
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Trying to save to: {save_path}")
                image.save(save_path)
                print(f"File saved successfully to {save_path}")
                
            breed = request.form.get('breed')
            age = request.form.get('age_months')
            health_records = request.form.get('Health_record')
            price = request.form.get('price')
            achivement = request.form.get('achiviements')
            
            # Create new pet
            new_pet = Pet(
                breed=breed,
                age_months=int(age),
                health_records=health_records,
                price=float(price),
                availability_status='Available',
                achivement=achivement,
                image=filename,
                description=f"A {breed} ({age} months old) with health status: '{health_records or 'No records'}' and achievements: '{achivement or 'None'}'."
            )
            
            db.session.add(new_pet)
            db.session.commit()
            
            flash(f"Dog {breed} added successfully!", "success")
            return redirect(url_for('admin'))
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            db.session.rollback()
            flash("Error in adding image", "error")
            return redirect(request.url)
            
    return render_template('add_dog.html')

@app.route('/delete_dog/<int:pet_id>', methods=['POST'])
def delete_dog(pet_id):
    try:
        pet = db.session.query(Pet).filter_by(pet_id=pet_id).first()
        
        if not pet:
            flash("Pet not found", "error")
            return redirect(url_for('admin'))
            
        if pet.image:
            image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', pet.image)
            
            try:
                if os.path.isfile(image_path):
                    os.remove(image_path)
                    print(f"Successfully deleted image: {image_path}")
                else:
                    print(f"Image file not found: {image_path}")
            except Exception as img_error:
                print(f"Error deleting image file: {str(img_error)}")
                
        db.session.delete(pet)
        db.session.commit()
        
        flash(f"{pet.breed} has been deleted successfully!", "success")
        return redirect(url_for('admin'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_dog: {str(e)}")
        flash(f"Error in deleting {pet.breed}", "error")
        return redirect(url_for('admin'))


def get_admin_cart_data():
    admin_cart_items = db.session.query(AdminCart).all()
    admin_cart_details = []
    for item in admin_cart_items:
        pet = db.session.query(Pet).filter_by(pet_id=item.pet_id).first()
        if pet:
            admin_cart_details.append({
                'id': item.id,
                'pet_id': pet.pet_id,
                'name': pet.breed,
                'price': float(pet.price),
                'total': float(pet.price),
                'image': pet.image
            })

    subtotal = sum(item['total'] for item in admin_cart_details)
    shipping = 500 if subtotal > 0 else 0
    gst = subtotal * 0.05
    sgst = subtotal * 0.05
    total = subtotal + shipping + gst + sgst

    return {
        'cart_details': admin_cart_details,
        'subtotal': subtotal,
        'shipping': shipping,
        'gst': gst,
        'sgst': sgst,
        'total': total
    }

# Admin Cart Routes
@app.route('/admin_cart', methods=['GET'])
def view_admin_cart():
    cart_data = get_admin_cart_data()
    return render_template(
        'admin_cart.html',
        admin_cart_items=cart_data['cart_details'],  # Changed from cart_items to admin_cart_items
        subtotal=cart_data['subtotal'],
        shipping=cart_data['shipping'],
        gst=cart_data['gst'],
        sgst=cart_data['sgst'],
        total=cart_data['total'],
        role='admin'
    )

@app.route('/admin/add_to_cart/<int:pet_id>', methods=['POST'])
def admin_add_to_cart(pet_id):
    try:
        pet = db.session.query(Pet).filter_by(pet_id=pet_id).first()
        if not pet:
            return "Pet not found", 404

        if pet.availability_status == 'sold':
            flash(f"{pet.breed} is no longer available for purchase.", "warning")
            return redirect(url_for('admin'))

        admin_cart_item = db.session.query(AdminCart).filter_by(pet_id=pet_id).first()
        if admin_cart_item:
            flash(f"{pet.breed} is already in your cart!", "info")
            return redirect(url_for('admin'))

        # Add new item to admin cart
        new_admin_cart_item = AdminCart(pet_id=pet_id)
        db.session.add(new_admin_cart_item)
        db.session.commit()
    
        flash(f"{pet.breed} has been added to your cart!", "success")
        return redirect(url_for('view_admin_cart'))

    except Exception as e:
        print(f"Error adding to admin cart: {e}")
        return "Error adding item to cart", 500

@app.route('/admin/delete_from_cart/<int:cart_item_id>', methods=['POST'])
def delete_from_admin_cart(cart_item_id):
    cart_item = db.session.query(AdminCart).filter_by(id=cart_item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('view_admin_cart'))

@app.route('/admin_policy', methods=['GET', 'POST'])
def admin_policy():
    return render_template('admin_policy.html')

def determine_cart_type():
    """
    Check which type of cart has items to determine if this is an admin or customer purchase
    Returns: 'admin' if items in admin cart, 'customer' if items in customer cart
    """
    admin_items = db.session.query(AdminCart).first()
    if admin_items:
        return 'admin'
    return 'customer'



@app.route('/shipping_details', methods=['GET', 'POST'])
def shipping_details():
    cart_type = determine_cart_type()

    if request.method == 'POST':
        flask_session['shipping_data'] = {
            'first_name': request.form.get('first_name'),
            'middle_name': request.form.get('middle_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'contact': request.form.get('contact'),
            'address': request.form.get('address'),
            'zip_code': request.form.get('zip_code'),
            'state': request.form.get('state'),
            'cart_type': cart_type  # Store cart type in session
        }
        return redirect(url_for('payment'))

    return render_template('shipping.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    shipping_data = flask_session.get('shipping_data', {})
    cart_type = shipping_data.get('cart_type')

    if request.method == 'POST':
        payment_option = request.form.get('payment_option')
        flask_session['payment_option'] = payment_option
        return redirect(url_for('success'))

    return render_template('payment.html', **shipping_data)

@app.route('/success')
def success():
    # Fixed typo in session key (removed space)
    shipping_data = flask_session.get('shipping_data', {})
    payment_option = flask_session.get('payment_option')
    cart_type = shipping_data.get('cart_type', 'customer')
    
    # Get cart data based on cart type
    if cart_type == 'admin':
        cart_data = get_admin_cart_data()
        cart_table = AdminCart
    else:
        cart_data = get_cart_data()
        cart_table = Cart

    current_date = datetime.today().strftime('%Y-%m-%d')
    expected_delivery_date = (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')

    template_data = {
        **shipping_data,
        'payment_option': payment_option,
        'current_date': current_date,
        'expected_delivery_date': expected_delivery_date,
        'role': cart_type,  # Add role to template data
        **cart_data
    }
    
    sale = Sale(
        buyer_name=f"{shipping_data.get('first_name', '')} {shipping_data.get('last_name', '')}",
        sale_date=datetime.now(),
        sale_price=cart_data['total'],
        payment_method=payment_option,
        invoice_number=str(datetime.now().timestamp()).replace('.', '')
    )
    db.session.add(sale)
    db.session.commit()
    
    for cart_detail in cart_data['cart_details']:
        sale_detail = Sale_detail(
        sale_id=sale.sale_id,
        breed_name=cart_detail['name'],
        price=cart_detail['price'],
        dog_id=cart_detail['pet_id']
        )
        db.session.add(sale_detail)

    db.session.commit()

    for cart_detail in cart_data['cart_details']:
        dog_sales = db.session.query(Dog_sales).filter_by(breed=cart_detail['name']).first()
        if not dog_sales:
         dog_sales = Dog_sales(
            breed=cart_detail['name'],
            quantity=1,
            price=cart_detail['price']
         )
         db.session.add(dog_sales)
        else:
         dog_sales.quantity += 1  # Increment quantity


    db.session.commit()
    
      # Update pet availability
    for cart_detail in cart_data['cart_details']:
        pet = db.session.query(Pet).filter_by(pet_id=cart_detail['pet_id']).first()
        if pet:
            pet.availability_status = 'sold'


    # Clear the appropriate cart
    db.session.query(cart_table).delete()
    db.session.commit()

    invoice_number = sale.invoice_number

   

    pet_details = "\n".join([f"""
        Pet: {item['name']}
        Price: ₹{item['price']}
        Quantity: {item.get('quantity', 1)}"""
        for item in cart_data['cart_details']
    ])

    try:
        msg = Message('Order Confirmation - PetCare', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[shipping_data['email']])
        msg.body = f"""
        Hello {shipping_data['first_name']},

        Thank you for your purchase!
        Here are your order details:

        Order Date: {current_date}
        Expected Delivery Date: {expected_delivery_date}

        Order Details:

        Invoice Number: {invoice_number}
        Payment Method: {payment_option}
        
        {pet_details}

        Total: ₹{cart_data['total']}
        
        We will notify you once your order has been shipped.

        Thank you for choosing PetHaven!
        """
        mail.send(msg)
        print("Order confirmation email sent successfully.")

    except Exception as e:
        print(f"Error sending email: {e}")

    return render_template('success.html', **template_data)
            
@app.route('/competition', methods=['GET'])
def competition_page():
    events = Event.query.all()  # Assuming Event is your database model
    today = date.today()

    for event in events:
        event_date = event.date
        event.is_active = event_date >= today  # Mark events as active or inactive

    return render_template('competition_page.html', events=events)

@app.route('/register_competition', methods=['GET', 'POST'])
def register_competition():
    # Fetch the events from the database
    events = Event.query.all()

    # Loop over events and update the 'is_active' status
    today = date.today()
    for event in events:
        event_date = event.date
        event.is_active = event_date >= today

    # Check for POST request (form submission)
    if request.method == 'POST':
        competition_id = request.form.get('competition-name')  # Retrieve event ID
        dog_name = request.form.get('dog-name')
        breed = request.form.get('breed')
        age = request.form.get('age')
        achievements = request.form.get('achievements')

        # Find the selected event by its ID
        event = Event.query.filter_by(id=competition_id).first()

        if event:
            # Save the registration
            new_registration = Registration(
                id=generate_dog_id(),
                event_id=event.id,  # Use the event's ID
                competition_name=event.name,  # Use event name from the found event
                dog_name=dog_name,
                breed=breed,
                age=age,
                achievements=achievements,
                status='Please complete payment process'  # Initially set as pending
            )

            db.session.add(new_registration)
            db.session.commit()

            flash("Successfully registered for the competition!", "regis")
            return redirect('/register_competition')
        else:
            flash("Invalid competition selected. Please try again.", "danger")

    # Return the registration page with event data
    return render_template('registration.html', events=events)


@app.route('/my-events')
def my_events():
    today = date.today()
    events = Event.query.all()
    registrations = Registration.query.all()
    carts=Cart.query.all()
    for registration in registrations:
        event_date = registration.event.date
        registration.event.is_active = event_date >= today
    
    return render_template('my_events.html', registrations=registrations, events=events,carts=carts)

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_registration(id):
    registration = Registration.query.get_or_404(id)
    if request.method == 'POST':
        registration.competition_name = request.form.get('competition-name')
        registration.dog_name = request.form.get('dog-name')
        registration.breed = request.form.get('breed')
        registration.age = request.form.get('age')
        registration.achievements = request.form.get('achievements')

        db.session.commit()
        flash("Registration updated successfully!", "my_events")
        return redirect('/my-events')

    return render_template('edit_registration.html', registration=registration)

@app.route('/delete/<string:id>', methods=['GET'])
def delete_registration(id):
    registration = Registration.query.get_or_404(id)
    db.session.delete(registration)
    db.session.commit()
    flash("Registration deleted successfully!", "my_events")
    return redirect('/my-events')

@app.route('/admin_events', methods=['GET'])
def admin_events():
    events = Event.query.all()
    today = date.today()
    for event in events:
        event.is_active = event.date >= today 
    return render_template('admin_events.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Get form data
        event_name = request.form.get('event-name')
        event_description = request.form.get('event-description')
        event_price = request.form.get('event-price')
        event_date = request.form.get('event-date')
        event_venue = request.form.get('event-venue')
        
        # Handle file upload
        event_image = request.files.get('event-image')
        
        if not event_image:
            flash('Event image is required!', 'danger')
            return redirect(request.url)
        
        # Choose a dynamic directory for uploads (e.g., 'uploads/')
        upload_directory = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)
        
        # Save the image to the dynamic directory
        image_filename = event_image.filename
        image_path = os.path.join(upload_directory, image_filename)
        image_path = image_path.replace(os.sep, '/')
        
        try:
            event_image.save(image_path)
        except Exception as e:
            flash(f"Error saving image: {e}", 'danger')
            return redirect(request.url)
        
        # Ensure that the other fields are not empty
        if not event_name or not event_description or not event_price or not event_date or not event_venue:
            flash('All fields are required!', 'danger')
            return redirect(request.url)
        
        # Create new event object and add it to the database
        try:
            new_event = Event(
                name=event_name,
                description=event_description,
                price=float(event_price),
                date=datetime.strptime(event_date, '%Y-%m-%d'),
                venue=event_venue,
                image=image_path  # Store the correct path to the image
            )
            
            # Add the event to the database
            db.session.add(new_event)
            db.session.commit()
            send_email_to_all_customers(event_name, event_date, event_venue)
            flash('Event added successfully!', 'Admin')
            return redirect(url_for('admin_events'))
        
        except Exception as e:
            flash(f"Error adding event: {e}", 'danger')

    return render_template('add_event.html')
def send_email_to_all_customers(event_name, event_date, event_venue):
    # Fetch all customers from the Customer table
    customers = Customer.query.all()

    for customer in customers:
        # Send email to each customer
        send_event_registration_email(
            customer_name=customer.first_name,
            customer_email=customer.email,
            event_name=event_name,
            event_date=event_date,
            event_venue=event_venue
        )

def send_event_registration_email(customer_name, customer_email, event_name, event_date, event_venue):
    # Compose the email body
    email_body = f"""
    Dear {customer_name},

    We are excited to announce a new event: {event_name}!

    Event Details:
    Event Name: {event_name}
    Date: {event_date}
    Venue: {event_venue}

    We encourage you to register for this event at the earliest. Don't miss out on this wonderful opportunity!

    Best regards,
    Pet Haven Team
    """

    # Send the email
    try:
        msg = Message(
            subject="New Event Announcement: Register Now!",
            recipients=[customer_email],
            body=email_body
        )
        mail.send(msg)
        print(f"Email sent to {customer_name} ({customer_email})")
    except Exception as e:
        print(f"Error sending email to {customer_name}: {e}")

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Get form data
        event_name = request.form.get('event-name')
        event_description = request.form.get('event-description')
        event_price = request.form.get('event-price')
        event_date = request.form.get('event-date')
        event_venue = request.form.get('event-venue')
        
        # Handle file upload
        event_image = request.files.get('event-image')
        
        if event_image:
            # Handle the image if it is updated
            upload_directory = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)
            
            image_filename = event_image.filename
            image_path = os.path.join(upload_directory, image_filename)
            image_path = image_path.replace(os.sep, '/')
            
            try:
                event_image.save(image_path)
            except Exception as e:
                flash(f"Error saving image: {e}", 'danger')
                return redirect(request.url)
            
            event.image = image_path  # Update image path
        
        # Update other fields
        event.name = event_name
        event.description = event_description
        event.price = float(event_price)
        event.date = datetime.strptime(event_date, '%Y-%m-%d')
        event.venue = event_venue
        
        try:
            # Commit changes to the database
            db.session.commit()
            flash('Event updated successfully!', 'Admin')
            return redirect(url_for('admin_events'))
        
        except Exception as e:
            flash(f"Error updating event: {e}", 'danger')
    
    return render_template('Admin_edit_event.html', event=event)
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    try:
        # Optionally, you can delete the image file as well (ensure the file is removed from the server)
        if event.image:
            image_path = os.path.join(app.root_path, event.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the event from the database
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'Admin')
        return redirect(url_for('admin_events'))
    
    except Exception as e:
        flash(f"Error deleting event: {e}", 'danger')
        return redirect(url_for('admin_events'))

@app.route('/cart_event')
def cart_event():
    registrations = Registration.query.all()
    cart_entries = CartEvent.query.all()
    events=Event.query.all()

    total_price = sum(entry.event_price for entry in cart_entries)
    
    return render_template('cart_event.html', cart_entries=cart_entries, total_price=total_price,registrations=registrations,events=events)

    
@app.route('/add_item_to_cart', methods=['POST'])
def add_item_to_cart():

    # Retrieve selected registration IDs
    id_list = request.form.getlist('registration_ids')  # ['1', '2', '3']
    print(request.form)
    print(id_list)
    
    # Initialize counters and flags
    added_count = 0
    invalid_payments = []

    # Process each ID
    for registration_id in id_list:
        registration = Registration.query.get(str(registration_id))
       
        
        if registration:
            # Validate payment status
            if registration.status.lower() in ['paid', 'pending']:
                invalid_payments.append(registration_id)
                continue  # Skip adding this registration
            
            # Fetch event price through the relationship
            event_price = registration.event.price  # Assuming relationship exists
            # Create a new Cart entry
            new_cart_item = CartEvent(
                registration_id=str(registration.id),
                event_price=event_price
            )
            db.session.add(new_cart_item)
            added_count += 1

    # Commit the changes for valid entries
    db.session.commit()
    
    # Flash appropriate messages
    if invalid_payments:
        flash(
            f"Some registrations were not added due to incomplete payment: {', '.join(invalid_payments)}.",
            category="warning"
        )
    
    if added_count > 0:
        flash(f"Successfully added {added_count} registrations to the cart!", category="success")
    else:
        flash("No registrations were added to the cart. Please check payment status.", category="error")
    
    return redirect('/cart_event')
    
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    # Find the cart entry by its ID
    cart_entry = CartEvent.query.get(cart_id)

    if cart_entry:
        # Delete the entry from the database
        db.session.delete(cart_entry)
        db.session.commit()
        flash(f"Item with ID {cart_id} removed from the cart.", category="success")
    else:
        flash(f"Item with ID {cart_id} not found.", category="error")

    # Redirect back to the cart page
    return redirect('/cart_event')


@app.route('/checkout_event', methods=['GET', 'POST'])
def checkout_event():
    # Fetch all cart items
    cart_items = CartEvent.query.all()

    registrations = (
        db.session.query(Registration)
        .join(CartEvent, CartEvent.registration_id == Registration.id)
        .all()
    )

    # Determine the payment status based on payment option
    payment_option = session.get('payment_option', 'Cash on Delivery')  # Default to 'Cash on Delivery'
    payment_status = "Pending" if payment_option == "Cash on Delivery" else "Paid"

    if request.method == 'POST':
        # Customer details
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        address = request.form.get('address')
        zip_code = request.form.get('zip_code')
        state = request.form.get('state')

        # Fetch competition names only for registrations in the cart
        competitions_registered = ", ".join(
            [reg.competition_name for reg in registrations]
        )

        # Calculate total amount from cart entries
        total_amount = sum(entry.event_price for entry in cart_items)

        # Save customer data
        new_customer = Customer(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            contact=contact,
            address=address,
            zip_code=zip_code,
            state=state,
            competitions_registered=competitions_registered,
            total_amount=total_amount
        )
        db.session.add(new_customer)
        db.session.commit()

        # Store customer and payment data in session
        session['shipping_data'] = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'contact': contact,
            'address': address,
            'zip_code': zip_code,
            'state': state,
            'competitions_registered': competitions_registered,
            'total_amount': total_amount
        }

        return redirect(url_for('payment_event'))  # Redirect to the payment page

    return render_template(
        'checkout_event.html',
        registrations=registrations,
        cart_items=cart_items
    )



@app.route('/payment_event', methods=['GET', 'POST'])
def payment_event():
    if request.method == 'POST':
        # Get payment option from the form
        payment_option = request.form.get('payment_option')
        session['payment_option'] = payment_option

        # Retrieve customer details from the session
        shipping_data = session.get('shipping_data', {})
        customer_email = shipping_data.get('email')

        # Fetch the customer using their email
        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            flash("Customer not found!", "error")
            return redirect(url_for('checkout_event'))

        # Get all cart items based on registration_id (assuming cart has a registration_id column)
        cart_items = CartEvent.query.all()

        # Create a list to store event details
        event_details = []
        for cart_item in cart_items:
            # Fetch the registration based on registration_id in Cart
            registration = Registration.query.filter_by(id=cart_item.registration_id).first()

            if registration:
                # Fetch the event based on event_id in Registration
                event = Event.query.get(registration.event_id)
                if event:
                    event_details.append({
                        "competition_name": event.name,
                        "event_id": event.id,
                        "registration_id": registration.id,
                        "venue": event.venue,
                        "date": event.date
                    })

        # Determine payment status
        payment_status = 'Pending' if payment_option == 'Cash On Delivery' else 'Paid'

        # Create a payment entry
        payment = Payment(
            customer_id=customer.id,
            amount=shipping_data.get('total_amount', 0),
            payment_method=payment_option,
            payment_status=payment_status
        )
        db.session.add(payment)
        db.session.commit()

        # Update registration status based on payment
        for cart_item in cart_items:
            registration = Registration.query.filter_by(id=cart_item.registration_id).first()
            if registration:
                registration.status = 'Paid' if payment_status == 'Paid' else 'Pending'
                db.session.add(registration)

        db.session.commit()
        

        # Send email notification with event details and payment status
        send_email_notification(
            customer_name=customer.first_name,
            customer_email=customer.email,
            event_details=event_details,
            payment_status=payment_status,
            payment_option=payment_option,
            amount_paid=shipping_data.get('total_amount'),
            amount_to_be_paid=None if payment_status == "Paid" else shipping_data.get('total_amount')
        )

        flash("Payment successful!", "success")
        return redirect(url_for('order_summary'))

    # Retrieve shipping data from session
    shipping_data = session.get('shipping_data', {})
    return render_template('payment_event.html', **shipping_data)

def send_email_notification(customer_name, customer_email, event_details, payment_status, payment_option, amount_paid, amount_to_be_paid=None):
    # Prepare details for each event
    event_details_str = ""
    for event in event_details:
        event_details_str += f"""
        <p><strong>Event Name:</strong> {event['competition_name']}<br>
        <strong>Date:</strong> {event['date'].strftime('%Y-%m-%d')}<br>
        <strong>Venue:</strong> {event['venue']}</p>
        """

    # Determine the payment content
    if payment_status.lower() == "paid":
        payment_details = f"""
        <p><strong>Payment Status:</strong> {payment_status}<br>
        <strong>Payment Option:</strong> {payment_option}<br>
        <strong>Amount Paid:</strong> ₹{amount_paid}</p>
        """
    else:
        payment_details = f"""
        <p><strong>Payment Status:</strong> {payment_status}<br>
        <strong>Payment Option:</strong> {payment_option}<br>
        <strong>Amount to be Paid:</strong> ₹{amount_to_be_paid}</p>
        """

    # Compose the email body (HTML format)
    email_body = f"""
    <html>
    <body>
    <p>Dear {customer_name},</p>

    <p>Thank you for registering for the following events:</p>
    {event_details_str}

    {payment_details}

    <p>We look forward to seeing you at the events at 10 a.m.</p>
    <p>Thank you for choosing Pet Haven!</p>

    <p>Best regards,<br>
    Pet Haven Team</p>
    </body>
    </html>
    """

    # Send the email
    try:
        msg = Message(
            subject="Event Registration Confirmation",
            recipients=[customer_email],
            html=email_body  # Send HTML email
        )
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")





@app.route('/order_summary')
def order_summary():
    registrations = Registration.query.all()
    cart_entries= CartEvent.query.all()
    
    total_price = sum(entry.event_price for entry in cart_entries)

    # Get customer details from session
    shipping_data = session.get('shipping_data', {})
    payment_option = session.get('payment_option')

    for cart_item in cart_entries:
            db.session.delete(cart_item)

    db.session.commit()
    

    return render_template('order_summary.html', 
                           registrations=registrations, 
                           total_price=total_price, 
                           
                           **shipping_data,
                           payment_option=payment_option,cart_entries=cart_entries)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)