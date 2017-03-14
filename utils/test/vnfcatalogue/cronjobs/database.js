var mysql = require('mysql');

var pool = mysql.createPool({
  host: 'localhost',
  user: 'myuser',
  password: 'mypassword',
  database: 'vnf_catalogue',
  connectionLimit: 50,
  supportBigNumbers: true,
  multipleStatements: true,
  dateStrings: 'date'
});

exports.pool = pool;
