from database import SessionLocal, User

db = SessionLocal()

doctor = User(
    username="doctor",
    password="doctor123",
    role="doctor"
)

db.add(doctor)

db.commit()

print("Doctor added successfully!")
