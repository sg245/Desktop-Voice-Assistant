from db import create_current_user_table, create_users_table, add_user, init_db

create_users_table()
create_current_user_table()
#if not add_user("admin", "1234"):
 #   print("Admin already exists")

#print("Database setup complete!")

if __name__ == "__main__":
    init_db()
    add_user("admin", "1234")
