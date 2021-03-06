// modules =================================================
var express = require('express');
var app     = express();
var mongoose= require('mongoose');
var passport = require('passport');
var flash  = require('connect-flash');
var http    = require('http');
var socketio = require('socket.io');

// configuration ===========================================
  
// config files
var db = require('./config/db');

require('./config/passport')(passport); 


var port = process.env.PORT || 8080; // set our port
mongoose.connect(db.url); // connect to our mongoDB database (uncomment after you enter in your own credentials in config/db.js)

app.configure(function() {
  
  // the order of app middleware is important - invoked sequentially!
  app.use(express.logger('dev')); // log every request to the console
  
  app.use(express.static(__dirname + '/public')); 	// set the static files location /public/img will be /img for users
  //app.use(express.logger('dev')); 					// log only non-public content
  app.use(express.bodyParser()); 						// have the ability to pull information from html in POST
  app.use(express.methodOverride()); 					// have the ability to simulate DELETE and PUT
  
  app.set('view engine', 'ejs'); // set up ejs for templating
  
  //setup passport
  app.use(express.cookieParser()); //sessions implemented with cookies
  app.use(express.session({secret: 'meandashisdashbest'})); //session secret
  app.use(passport.initialize());
  app.use(passport.session()); //persistent logins
  app.use(flash()); // flash messages stored in session
});

// routes ==================================================
var routes = require('./app/routes');
routes(app, passport); // configure our routes

// start app ===============================================

var server = http.createServer(app);
var io = socketio.listen(server);

server.listen(port, function() { // startup our app at http://localhost:port
  console.log("listening...");
});

io.sockets.on('connection', routes.vote);

console.log('Magic happens on port ' + port); 			// shoutout to the user
exports = module.exports = app; 						// expose app

