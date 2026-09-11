import os
import sys

# Add project root and backend to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.department import Department


def seed_database():
    print("[SEED] Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("[SEED] Seeding default hospital departments...")
        default_departments = [
            {"name": "General Medicine", "description": "Primary healthcare and general clinical consultations"},
            {"name": "Cardiology", "description": "Heart and cardiovascular system medical services"},
            {"name": "Pediatrics", "description": "Child health and medical care"},
            {"name": "Orthopedics", "description": "Bone, joint, and musculoskeletal medical department"},
            {"name": "Intensive Care Unit (ICU)", "description": "Critical care services and continuous monitoring"},
            {"name": "Neurology", "description": "Brain, spinal cord, and nervous system specialty"},
            {"name": "Emergency", "description": "24/7 Trauma and emergency triage services"},
        ]

        for dept_data in default_departments:
            existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
            if not existing:
                dept = Department(name=dept_data["name"], description=dept_data["description"])
                db.add(dept)
                print(f"  + Added department: {dept_data['name']}")

        db.commit()

        print("[SEED] Seeding default administrative accounts...")
        default_users = [
            {
                "username": "admin",
                "email": "admin@hospital.local",
                "password": "AdminPass2026!",
                "role": "ADMIN",
            },
            {
                "username": "reception",
                "email": "reception@hospital.local",
                "password": "ReceptionPass2026!",
                "role": "RECEPTIONIST",
            },
            {
                "username": "doctor_smith",
                "email": "dr.smith@hospital.local",
                "password": "DoctorPass2026!",
                "role": "DOCTOR",
            },
        ]

        for user_data in default_users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                )
                db.add(user)
                print(f"  + Added user: {user_data['username']} ({user_data['role']})")

        db.commit()
        print("[SEED SUCCESS] Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR] Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
