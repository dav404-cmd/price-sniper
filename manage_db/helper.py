from db_manager import DataBase
from pathlib import Path
if __name__ == "__main__":

    path = Path(__file__).resolve().parents[1]
    db_dir_path = path / "database"
    db_path = db_dir_path / "listing.db"
    test_db_path = db_dir_path / "test.db"
    db = DataBase(test_db_path,is_test=True)
    db.delete_all()
    db.close()

    print(f"Deleted all records from: {db_path}")
