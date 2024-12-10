require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

const createTables = `
  -- Users table
  CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Items table
  CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    upc VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 0,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Transactions table
  CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    user_id INTEGER REFERENCES users(id),
    quantity_changed INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
`;

const seedData = `
  -- Insert admin user (password is 'admin123' - you should change this)
  INSERT INTO users (username, email, password_hash, is_admin)
  VALUES ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4WAhOv3Q8S', true)
  ON CONFLICT (username) DO NOTHING;

  -- Insert sample items
  INSERT INTO items (upc, name, description, quantity, min_quantity, location)
  VALUES 
    ('123456789012', 'Test Item 1', 'Description for test item 1', 10, 5, 'Shelf A1'),
    ('123456789013', 'Test Item 2', 'Description for test item 2', 15, 8, 'Shelf B2'),
    ('123456789014', 'Test Item 3', 'Description for test item 3', 20, 10, 'Shelf C3')
  ON CONFLICT (upc) DO NOTHING;
`;

async function setupDatabase() {
  try {
    console.log('Creating tables...');
    await pool.query(createTables);
    console.log('Tables created successfully!');

    console.log('Seeding database...');
    await pool.query(seedData);
    console.log('Database seeded successfully!');

  } catch (err) {
    console.error('Error setting up database:', err);
  } finally {
    await pool.end();
  }
}

// Run the setup if this file is run directly
if (require.main === module) {
  setupDatabase();
}

module.exports = { setupDatabase }; 