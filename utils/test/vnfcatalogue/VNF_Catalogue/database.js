/*******************************************************************************
 * Copyright (c) 2017 Kumar Rishabh and others.
 *
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Apache License, Version 2.0
 * which accompanies this distribution, and is available at
 * http://www.apache.org/licenses/LICENSE-2.0
 *******************************************************************************/

var mysql = require('mysql');

var pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'iiit123',
  database: 'vnf_catalogue',
  connectionLimit: 50,
  supportBigNumbers: true,
  multipleStatements: true,
  dateStrings: 'date'
});

exports.pool = pool;
