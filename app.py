from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
import os

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'malshanibandaranayake91@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'mksn gkuy luql ldtx')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'malshanibandaranayake91@gmail.com')

mail = Mail(app)

# Configure Flask app and database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:@localhost/booking_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
db = SQLAlchemy(app)

# Define the Token model
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    used = db.Column(db.Boolean, default=False)

# Define the Appointment model
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    hospital = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(100), nullable=False)
    deciese_type = db.Column(db.String(100), nullable=False)

# Define the Feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

# Define the Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()
    # Initialize tokens from 1 to 50
    if Token.query.count() == 0:
        for num in range(1, 51):
            token = Token(number=num)
            db.session.add(token)
        db.session.commit()

# Load the model
model = load_model('model.h5')

def prepare_image(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img /= 255.0
    return img


# Route for home page (Upload an image of a foot-corn or athlete-foot)
@app.route('/', methods=['GET', 'POST'])
def index():
    doctors_list = Doctor.query.all()  # Fetch doctors' details from the database
    if request.method == 'POST':
        img = request.files['file']
        img_path = "static/" + img.filename
        img.save(img_path)

        img = prepare_image(img_path)
        prediction = model.predict(img)
        class_index = np.argmax(prediction[0])  # Get the index of the highest probability
        class_names = ['athlete-foot', 'foot-corn', 'invalid-image']  
        result = class_names[class_index]

        return render_template('result.html', result=result, img_path=img_path)
    return render_template('index.html', doctors=doctors_list)


# Route for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for feedback page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        feedback_text = request.form['feedback']
        
        new_feedback = Feedback(name=name, text=feedback_text)
        db.session.add(new_feedback)
        db.session.commit()
        
        return redirect(url_for('feedback'))

    feedbacks = Feedback.query.all()
    return render_template('feedback.html', feedbacks=feedbacks)

# Route to display treatment based on image classification
@app.route('/treatment/<result>')
def treatment(result):
    if result == 'foot-corn':
        return "Treatment: Surgery, Use corn pads"
    elif result == 'athlete-foot':
        return "Treatment: Washing feet well, Use Tea-tree oil, Use Clotrimazole "
    elif result == 'invalid-image ':
        return "Treatment: This one not define"
    else:
        return "This one not define"


# Route to book an appointment
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        doctor_name = request.form['doctor_name']
        appointment_time = request.form['appointment_time']
        hospital = request.form['hospital']
        patient_email = request.form['patient_email']
        deciese_type = request.form['deciese_type']
        
        try:
            appointment_time = datetime.strptime(appointment_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            return "Invalid date format. Please use 'YYYY-MM-DDTHH:MM'."

        # Get the next available token number
        token = Token.query.filter_by(used=False).first()
        if token is None:
            return "No available tokens. Please try again later."

        # Mark the token as used
        token.used = True
        db.session.commit()

        new_appointment = Appointment(
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_time=appointment_time,
            hospital=hospital,
            patient_email=patient_email,
            deciese_type=deciese_type 
        )
        db.session.add(new_appointment)
        db.session.commit()

        # Generate doctor's arrival time
        doctor_arrival_time = '10:00 AM'

        # Send email to the patient
        msg = Message('Appointment Confirmation',
                      recipients=[patient_email])
        msg.body = f"Dear {patient_name},\n\nYour appointment with Dr. {doctor_name} at {hospital} has been confirmed.\n\nToken Number: {token.number}\nDoctor's Arrival Time: {doctor_arrival_time}\n\nThank you for choosing our service."
        mail.send(msg)

        flash('Appointment booked successfully! Confirmation email sent.', 'success')
        session['patient_name'] = patient_name  # Save patient name to session
        return redirect(url_for('patient_appointments'))
    return render_template('appointment.html')

# Route for a patient to view their appointments
@app.route('/patient_appointments')
def patient_appointments():
    if 'patient_name' not in session:
        return redirect(url_for('login'))

    patient_name = session['patient_name']
    appointments = Appointment.query.filter_by(patient_name=patient_name).all()
    return render_template('patient_appointments.html', appointments=appointments)

# Route for admin to view all appointments
@app.route('/admin_main_page')
def admin_main_page():
    appointments = Appointment.query.all()
    return render_template('admin_main_page.html', appointments=appointments)

# Route for admin to view all appointments
@app.route('/admin_view_appointments')
def admin_view_appointments():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
        
    appointments = Appointment.query.all()
    return render_template('admin_view_appointments.html', appointments=appointments)

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'malshani' and password == '12345':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_main_page'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

# Admin logout route
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# Route to view doctor details
@app.route('/doctors')
def doctors():
    doctors_list = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors_list)

if __name__ == '__main__':
    app.run(debug=True)
