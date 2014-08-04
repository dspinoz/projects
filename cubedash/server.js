// modules =================================================
var express = require('express');
var app     = express();
var http    = require('http');

// configuration ===========================================
  
var port = process.env.PORT || 8080; // set our port

app.configure(function() {
  
  // the order of app middleware is important - invoked sequentially!
  app.use(express.logger('dev')); // log every request to the console
  
  app.use(express.static(__dirname + '/public')); 	// set the static files location /public/img will be /img for users
  //app.use(express.logger('dev')); 					// log only non-public content
});

// routes ==================================================

// start app ===============================================

var server = http.createServer(app);

server.listen(port, function() { // startup our app at http://localhost:port
  console.log("listening...");
});

console.log('Magic happens on port ' + port); // shoutout to the user
exports = module.exports = app; 						  // expose app

