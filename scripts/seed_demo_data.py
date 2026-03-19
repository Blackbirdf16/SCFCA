"""
SCFCA PoC: Demo database seeder for SQLite.
Seeds demo users, cases, assets, tickets, approvals, audit events, and documents.
Passwords are for demo use only.
"""
from backend.core.database import engine, Base, SessionLocal
from backend.users.models import User
from backend.auth.schemas import Role
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # --- Users ---
    users = [
        User(username="alice", password_hash=hash_password("alice123"), role=Role.case_handler, is_active=True),
        User(username="bob", password_hash=hash_password("bob123"), role=Role.administrator, is_active=True),
        User(username="eve", password_hash=hash_password("eve123"), role=Role.administrator, is_active=True),
        User(username="carol", password_hash=hash_password("carol123"), role=Role.auditor, is_active=True),
    ]
    db.add_all(users)
    db.commit()
    db.refresh(users[0])
    db.refresh(users[1])
    db.refresh(users[2])
    db.refresh(users[3])

    # (Other seeding for cases, assets, tickets, etc. is currently disabled due to missing models)
    approval1 = Approval(ticket_id=ticket1.id, approver_id=users[2].id, approved=True)
    approval2 = Approval(ticket_id=ticket2.id, approver_id=users[1].id, approved=False)
    db.add_all([approval1, approval2])
    db.commit()

    # --- Audit Events ---
    audit1 = AuditEvent(actor_id=users[1].id, action="login", entity_type="user", entity_id=users[1].id, details="User bob logged in.")
    audit2 = AuditEvent(actor_id=users[0].id, action="case_created", entity_type="case", entity_id=case1.id, details="Case Operation Hydra created.")
    audit3 = AuditEvent(actor_id=users[1].id, action="ticket_created", entity_type="ticket", entity_id=ticket1.id, details="Transfer request ticket created.")
    db.add_all([audit1, audit2, audit3])
    db.commit()

    # --- Documents ---
    doc1 = DocumentRecord(case_id=case1.id, filename="evidence1.pdf", filehash="abc123hash", upload_date=datetime.utcnow())
    doc2 = DocumentRecord(case_id=case2.id, filename="report2.docx", filehash="def456hash", upload_date=datetime.utcnow())
    db.add_all([doc1, doc2])
    db.commit()

    db.close()
    print("Demo data seeded.")

if __name__ == "__main__":
    seed()
