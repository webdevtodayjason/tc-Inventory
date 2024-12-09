const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

// Test the connection
async function testConnection() {
  try {
    const client = await pool.connect();
    console.log('Connected to PostgreSQL database');
    await client.release();
  } catch (err) {
    console.error('Error connecting to the database:', err);
  }
}

module.exports = { pool, testConnection }; 