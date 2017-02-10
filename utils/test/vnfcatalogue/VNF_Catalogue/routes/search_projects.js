/*******************************************************************************
 * Copyright (c) 2017 Kumar Rishabh and others.
 *
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Apache License, Version 2.0
 * which accompanies this distribution, and is available at
 * http://www.apache.org/licenses/LICENSE-2.0
 *******************************************************************************/

var express = require('express');
var router = express.Router();

router.get('/', function(req, res) {
  var tags = req.param('tags');
  console.log(tags);
  res.render('search_projects', { title: 'Express' });
});

module.exports = router;
