USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

PROPERTIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zipcode TEXT NOT NULL,
    square_feet REAL NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms REAL NOT NULL,
    year_built INTEGER NOT NULL,
    last_sale_price REAL,
    last_sale_date TEXT,
    created_at TEXT NOT NULL
);
"""

PREDICTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    property_id INTEGER,
    input_data TEXT NOT NULL,
    predicted_price REAL NOT NULL,
    future_price REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (property_id) REFERENCES properties(id)
);
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);",
    "CREATE INDEX IF NOT EXISTS idx_properties_state ON properties(state);",
    "CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);",
]

ALL_TABLES = [USERS_TABLE_SQL, PROPERTIES_TABLE_SQL, PREDICTIONS_TABLE_SQL]
