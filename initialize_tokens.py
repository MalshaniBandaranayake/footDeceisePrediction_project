from app import db, Appointment
import random

def initialize_tokens():
    # Check if tokens already exist
    existing_tokens = Appointment.query.filter(Appointment.token_number.isnot(None)).all()
    if existing_tokens:
        print("Tokens already initialized.")
        return

    # Generate token numbers
    tokens = list(range(1, 51))

    for token in tokens:
        # Create a new appointment with the token number
        appointment = Appointment(token_number=token)
        db.session.add(appointment)
    
    db.session.commit()
    print("Tokens initialized successfully.")

if __name__ == "__main__":
    initialize_tokens()
