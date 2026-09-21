from database import SessionLocal
from services.risk_automation import run_risk_review


def main() -> None:
    db = SessionLocal()

    try:
        result = run_risk_review(db)

        print("Risk review completed.")
        print(f"Customers scanned: {result.customers_scanned}")
        print(f"High-risk customers: {result.high_risk_customers}")
        print(f"Tasks created: {result.tasks_created}")
        print(f"Tasks skipped: {result.tasks_skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()