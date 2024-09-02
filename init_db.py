from app import app, db
from app import Doctor

# Create the application context
with app.app_context():
    # Create the tables if they don't exist
    db.create_all()

    # Add doctor records
    doctor1 = Doctor(name='Hemal Perera', specialty='foot-corn', image_filename='hemal_perera.jpg')
    doctor2 = Doctor(name='Kenul Sembukutti', specialty='foot-corn', image_filename='kenul_sembukutti.jpg')
    doctor3 = Doctor(name='Sudarshan Mendis', specialty='athlete-foot', image_filename='sudarshan_mendis.jpg')
    doctor4 = Doctor(name='Apsara Haputhanthri', specialty='athlete-foot', image_filename='apsara_haputhanthri.jpg')

    db.session.add_all([doctor1, doctor2, doctor3, doctor4])
    db.session.commit()

    print("Doctors have been added to the database.")
