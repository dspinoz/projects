#!/usr/bin/env node

// modules =================================================
var express = require('express');
var request = require('request');
var app     = express();

// configuration ===========================================
  
var port = process.env.PORT || 8080; // set our port

app.configure(function() {
  
  // the order of app middleware is important - invoked sequentially!
  app.use(express.logger('dev')); // log every request to the console
  
  app.use(express.static(__dirname + '/public')); 	// set the static files location
  //app.use(express.logger('dev')); 					// log only non-public content
});

// routes to cube server ===========================================

var cubeHost = '10.1.1.16',
    cubePort = 1081;
    
app.get('/types', function(req,res) {
  req.pipe(request('http://' +cubeHost +':'+ cubePort+ '/1.0' + req.originalUrl)).pipe(res);
});
app.get('/metric', function(req,res) {
  req.pipe(request('http://' +cubeHost +':'+ cubePort+ '/1.0' + req.originalUrl)).pipe(res);
});

// static files  ==================================================

// TBD under development use full source, otherwise use min

app.get('/jquery.js', function(req,res) {
  res.sendfile('node_modules/jquery/dist/jquery.js');
});

app.get('/bootstrap.js', function(req,res) {
  res.sendfile('node_modules/bootstrap/dist/js/bootstrap.js');
});

app.get('/bootstrap.css', function(req,res) {
  res.sendfile('node_modules/bootstrap/dist/css/bootstrap.css');
});
app.get('/bootstrap.css.map', function(req,res) {
  res.sendfile('node_modules/bootstrap/dist/css/bootstrap.css.map');
});

app.get('/d3.js', function(req, res) {
  res.sendfile('node_modules/d3/d3.js')
});

app.get('/queue.js', function(req, res) {
  res.sendfile('node_modules/queue-async/queue.js')
});

app.get('/cubism.js', function(req, res) {
  res.sendfile('node_modules/cubism/cubism.v1.js')
});

app.get('/crossfilter.js', function(req, res) {
  res.sendfile('node_modules/crossfilter/crossfilter.js')
});

// start app ===============================================

app.listen(port, function() { // startup our app at http://localhost:port
  console.log("listening...");
});

console.log('Magic happens on port ' + port); // shoutout to the user
exports = module.exports = app; 						  // expose app

