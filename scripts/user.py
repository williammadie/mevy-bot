import getpass
import bcrypt
import psycopg2


def prompt(prompt_text, default=None):
    if default:
        return input(f"{prompt_text} [{default}]: ") or default
    return input(f"{prompt_text}: ")


def main():
    print("🚀 User Insertion CLI\n")

    # Prompt for DB connection info
    db_host = prompt("DB host", "localhost")
    db_port = prompt("DB port", "5432")
    db_name = prompt("DB name", "mevy_bot")
    db_user = prompt("DB user", "postgres")
    db_password = getpass.getpass("DB password: ")

    # Prompt for user info
    print("\n👤 New User Details")
    user_name = prompt("Name")
    user_email = prompt("Email")
    user_password = getpass.getpass("Password: ")

    # Hash the password
    hashed = bcrypt.hashpw(user_password.encode("utf8"),
                           bcrypt.gensalt()).decode()

    # Connect and insert
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, password_hash, email) VALUES (%s, %s, %s);",
            (user_name, hashed, user_email)
        )
        conn.commit()
        cur.close()
        conn.close()
        print("\n✅ User inserted successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
