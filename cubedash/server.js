// modules =================================================
var express = require('express');
var app     = express();

// configuration ===========================================
  
var port = process.env.PORT || 8080; // set our port

app.configure(function() {
  
  // the order of app middleware is important - invoked sequentially!
  app.use(express.logger('dev')); // log every request to the console
  
  app.use(express.static(__dirname + '/public')); 	// set the static files location
  //app.use(express.logger('dev')); 					// log only non-public content
});

// routes ==================================================

app.get('/d3.js', function(req, res) {
  res.sendfile('node_modules/d3/d3.js')
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

