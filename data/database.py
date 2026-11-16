import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

DATABASE_PATH = DATA_DIR / "legislative_aid.db"


def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():

    DATA_DIR.mkdir(exist_ok=True)

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS programs (
                program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_name TEXT NOT NULL,
                agency TEXT NOT NULL,
                description TEXT,
                eligible_entities TEXT,
                eligible_locations TEXT,
                funding_amount TEXT,
                application_deadline TEXT,
                official_url TEXT,
                eligibility_status TEXT DEFAULT 'unverified',
                last_verified TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS eligibility_requirements (
                requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER NOT NULL,
                requirement TEXT NOT NULL,
                requirement_type TEXT,
                FOREIGN KEY (program_id)
                    REFERENCES programs(program_id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS program_tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (program_id)
                    REFERENCES programs(program_id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER NOT NULL,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                date_accessed TEXT,
                FOREIGN KEY (program_id)
                    REFERENCES programs(program_id)
                    ON DELETE CASCADE
            )
        """)


def add_program(
    program_name,
    agency,
    description,
    eligible_entities,
    eligible_locations,
    official_url = None,
    funding_amount = None,
    application_deadline = None,
    eligibility_status = "unverified",
    last_verified = None
):

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO programs (
                program_name,
                agency,
                description,
                eligible_entities,
                eligible_locations,
                funding_amount,
                application_deadline,
                official_url,
                eligibility_status,
                last_verified
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            program_name,
            agency,
            description,
            eligible_entities,
            eligible_locations,
            funding_amount,
            application_deadline,
            official_url,
            eligibility_status,
            last_verified
        ))

        return cursor.lastrowid


def add_program_tag(program_id, tag):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO program_tags (
                program_id,
                tag
            )
            VALUES (?, ?)
        """, (program_id, tag))


def add_requirement(
    program_id,
    requirement,
    requirement_type
):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO eligibility_requirements (
                program_id,
                requirement,
                requirement_type
            )
            VALUES (?, ?, ?)
        """, (
            program_id,
            requirement,
            requirement_type
        ))


def add_program_source(
    program_id,
    source_name,
    source_url,
    date_accessed = None
):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO sources (
                program_id,
                source_name,
                source_url,
                date_accessed
            )
            VALUES (?, ?, ?, ?)
        """, (
            program_id,
            source_name,
            source_url,
            date_accessed
        ))


def get_all_programs():

    with get_connection() as connection:

        programs = connection.execute("""
            SELECT *
            FROM programs
            ORDER BY program_name
        """).fetchall()

        return [dict(program) for program in programs]


def get_program_tags(program_id):

    with get_connection() as connection:

        tags = connection.execute("""
            SELECT tag
            FROM program_tags
            WHERE program_id = ?
        """, (program_id,)).fetchall()

        return [row["tag"] for row in tags]


def get_program_requirements(program_id):

    with get_connection() as connection:

        requirements = connection.execute("""
            SELECT requirement, requirement_type
            FROM eligibility_requirements
            WHERE program_id = ?
        """, (program_id,)).fetchall()

        return [dict(row) for row in requirements]


def get_program_sources(program_id):

    with get_connection() as connection:

        sources = connection.execute("""
            SELECT source_name, source_url, date_accessed
            FROM sources
            WHERE program_id = ?
        """, (program_id,)).fetchall()

        return [dict(row) for row in sources]


if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")

    print("Location:", DATABASE_PATH)
