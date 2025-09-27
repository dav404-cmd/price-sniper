from manage_db.db_manager import PostgresDB

if __name__ == "__main__":
    db = PostgresDB()
    db.show_all(readable=True)
    db.count_row()
    db.invalid_rows()
    db.close()

