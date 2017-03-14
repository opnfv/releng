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
var async = require('async');


var renderer = function(res, err, results) {
    console.log(results);
    res.render('search_projects', { title: 'Express', json: results });
}

var get_tags = function(result, callback) {
    db_pool.getConnection(function(err, connection) {
        sql_query = 'select tag_name from tag where tag_id in (select tag_id from vnf_tags where vnf_id = ' + result['vnf_id'] + ') limit 5';
        // TODO find why it works and not above
        connection.query(sql_query, function (error, results, fields) {
            console.log(results);
            result['tags'] = results;
            callback(null, result);
            //connection.release();
            if (error) throw error;
        });
    });
}


var get_images = function(result, callback) {
    db_pool.getConnection(function(err, connection) {
        sql_query = 'select photo_url from photo where photo_id = ' + result['photo_id'];
        // TODO find why it works here and not when declared outside the method
        console.log(sql_query);
        connection.query(sql_query, function (error, results, fields) {
            console.log(results[0].photo_url);
            result['photo_url'] = results[0].photo_url;
            callback(null, result);
            //connection.release();
            if (error) throw error;
        });
    });
}

var sql_data = function(tags, renderer, res) {
    var tag_array = "\'" + tags.map(function (item) { return item; }).join("\',\'") + "\'";
    console.log(tag_array);
    var condition = '';
    db_pool.getConnection(function(err, connection) {
        sql_query = 'select tag_id from tag where tag_name in (' + tag_array + ')';
        connection.query(sql_query, function (error, results, fields) {
            condition = 'SELECT * FROM vnf as v';
            for (var i in results) {
                condition += (i == 0) ? ' WHERE ' : ' AND ';
                condition += 'v.vnf_id IN (SELECT vnf_id from vnf_tags where tag_id = ' + results[i]['tag_id'] + ')';
            }

            connection.query(condition, function (error, results, fields) {
                    console.log(results);
                    async.map(results, get_images, function(error, results) {
                        async.map(results, get_tags, renderer.bind(null, res));
                    });
                    //connection.release();
                    if (error) throw error;
            });

            connection.release();
            if (error) throw error;
        });
    });

}

router.get('/', function(req, res) {

  console.log(typeof(req.param('tags')));
  var tags = req.param('tags');

  if(tags) {
    tags = tags.toLowerCase().split(/[ ,]+/);
    console.log(tags);
    sql_data(tags, renderer, res);
  } else {
    res.render('search_projects', { title: 'Express', json: false});
  }

});

module.exports = router;
