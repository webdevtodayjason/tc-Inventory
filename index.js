require('dotenv').config();
const { pool, testConnection } = require('./database');

// Test the connection
testConnection();

// Example query
async function exampleQuery() {
  try {
    const result = await pool.query('SELECT NOW()');
    console.log('Query result:', result.rows[0]);
  } catch (err) {
    console.error('Query error:', err);
  }
}

exampleQuery(); 