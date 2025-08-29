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
    print("====ROW COUNT====")
    db.count_row()

    print("====Find by url====")
    row1 = db.find_by_url("https://slickdeals.net/f/18533692-prime-samsers-foldable-bluetooth-keyboard-portable-folding-keyboard-for-ipad-iphone-macbook-android-pc-black-16-63-free-shipping?src=SDSearchv3&attrsrc=Thread%3AExpired%3AFalse%7CSearch%3AType%3Anormal%7CSearch%3ASort%3Arelevance%7CSearch%3AHideExpired%3Atrue")
    print(row1)
    print("====Find by title====")
    rows = db.search_by_title("Acer Aspire 3 Laptop",limit=3)
    for item in rows:
        print(f"{item['title']} | Price: ${item['price']} |Discount(%): {item['discount_percentage']}| Store: {item['store']} | URL: {item['url']}")
    print("====Find by category====")
    rows2 = db.search_by_category("apparel",limit = 3)
    for item in rows2:
        print(
            f"{item['title']} | Price: ${item['price']} |Discount(%): {item['discount_percentage']}| Store: {item['store']} | URL: {item['url']}")
    db.close()

