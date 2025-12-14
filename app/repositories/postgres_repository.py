import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class PostgresRepository:
    def __init__(self):
        # Load configuration from environment variables
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", 5432))
        self.dbname = os.getenv("POSTGRES_DB", "dws_tradestore")
        self.user = os.getenv("POSTGRES_USER", "dws_user")
        self.password = os.getenv("POSTGRES_PASSWORD", "dwsuser1234")

        # Connect to PostgreSQL
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Connected to PostgreSQL")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise

    def create_tables(self):
        """Create the required tables if they do not exist."""
        try:
            # Example table: trades
            create_trades_table = """
            DROP TABLE IF EXISTS trades;
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                trade_id VARCHAR(50) NOT NULL UNIQUE,
                version INT NOT NULL,
                counter_party_id VARCHAR(50) NOT NULL,
                book_id VARCHAR(50) NOT NULL,
                maturity_date DATE NOT NULL,
                created_date DATE NOT NULL,
                expired BOOLEAN NOT NULL DEFAULT FALSE
            );
            """
            self.cursor.execute(create_trades_table)
            print("Table 'trades' created or already exists")
            
            # You can add more tables here, e.g., users, portfolios, etc.
            # self.cursor.execute(<another CREATE TABLE statement>)
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("PostgreSQL connection closed")
