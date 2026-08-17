from flask import Flask
import socket
import psycopg2
import os

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "devops-sre-postgres"),
        database=os.getenv("DB_NAME", "devopsdb"),
        user=os.getenv("DB_USER", "devops"),
        password=os.getenv("DB_PASSWORD", "devops_password"),
        port=os.getenv("DB_PORT", "5432")
    )


@app.route("/")
def home():
    return {
        "message": "DevOps SRE Demo Application",
        "hostname": socket.gethostname(),
        "status": "healthy"
    }


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


@app.route("/db-health")
def db_health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result[0] == 1:
            return {
                "database": "PostgreSQL",
                "status": "healthy"
            }

    except Exception as error:
        return {
            "database": "PostgreSQL",
            "status": "unhealthy",
            "error": str(error)
        }, 500

@app.route("/db-test")
def db_test():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_items (
                id SERIAL PRIMARY KEY,
                message VARCHAR(255) NOT NULL
            );
        """)

        cursor.execute(
            "INSERT INTO test_items (message) VALUES (%s) RETURNING id, message;",
            ("Docker PostgreSQL integration successful",)
        )

        result = cursor.fetchone()
        connection.commit()

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "database": "PostgreSQL",
            "id": result[0],
            "message": result[1]
        }

    except Exception as error:
        return {
            "status": "failed",
            "database": "PostgreSQL",
            "error": str(error)
        }, 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
