from app.database import Base, SessionLocal, engine
from app.repository import Repository
from app.services import RadarService


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        opportunities, run = RadarService().run_scan(Repository(db))
        print(f"completed run {run.id} with {len(opportunities)} opportunities")
    finally:
        db.close()
