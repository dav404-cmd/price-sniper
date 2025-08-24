from db_manager import DataBase
from pathlib import Path

from utils.logger import get_logger

db_helper_log = get_logger("DB_helper")

if __name__ == "__main__":

    path = Path(__file__).resolve().parents[1]
    db_dir_path = path / "database"
    db_path = db_dir_path / "listing.db"
    test_db_path = db_dir_path / "test.db"


    """Do stuffs in db here """
    db = DataBase(db_path)

    db.count_row()
    db.close()

    db_helper_log.critical(f"Deleted all records from: {db_path}")
