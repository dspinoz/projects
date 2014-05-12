// models
var Todo = require('./models/todo');

module.exports = function(app, passport) {
  // handle things like api calls
  // authentication routes
  
  // home page with login links
  app.get('/', function(req, res) {
    res.render('index.ejs');
  });
  
  // ============================PASSPORT===============================

  // login form
  app.get('/login', function(req, res) {
    // render the page, but pass flash data if it exists
    res.render('login.ejs', { message: req.flash('loginMessage') });
  });
  
  // process the login form
  app.post('/login', passport.authenticate('local-login', {
    successRedirect: '/profile', //secure profile view
    failureRedirect: '/login', //back to signup
    failureFlash: true //flash messages
  }));
  
  // signup form
  app.get('/signup', function(req, res) {
    res.render('signup.ejs', { message: req.flash('signupMessage') });
  });
  
  // process the signup form
  app.post('/signup', passport.authenticate('local-signup', {
    successRedirect: '/profile', // secure profile view
    failureRedirect: '/signup', // back to signup
    failureFlash: true //flash messages
  }));
  
  // profiles
  // PROTECTED: must be logged in to view
  //            verified by using route middleware
  app.get('/profile', isLoggedIn, function(req, res) {
    res.render('profile.ejs', { user: req.user } );/* user from the session */
  });
  
  // logout
  app.get('/logout', function(req, res) {
    req.logout();
    res.redirect('/');
  });
  
  // ============================TODO===============================
  
  	// api ---------------------------------------------------------------------
	// get all todos
	app.get('/api/todos', function(req, res) {

		// use mongoose to get all todos in the database
		Todo.find(function(err, todos) {

			// if there is an error retrieving, send the error. nothing after res.send(err) will execute
			if (err)
				res.send(err)

			res.json(todos); // return all todos in JSON format
		});
	});

	// create todo and send back all todos after creation
	app.post('/api/todos', function(req, res) {

		// create a todo, information comes from AJAX request from Angular
		Todo.create({
			text : req.body.text,
			done : false
		}, function(err, todo) {
			if (err)
				res.send(err);

			// get and return all the todos after you create another
			Todo.find(function(err, todos) {
				if (err)
					res.send(err)
				res.json(todos);
			});
		});

	});

	// delete a todo
	app.delete('/api/todos/:todo_id', function(req, res) {
		Todo.remove({
			_id : req.params.todo_id
		}, function(err, todo) {
			if (err)
				res.send(err);

			// get and return all the todos after you create another
			Todo.find(function(err, todos) {
				if (err)
					res.send(err)
				res.json(todos);
			});
		});
	});
  
  // ============================PUBLIC===============================
  
  // public views - automatically rendered by visiting http://server/*.html
  // custom public routes
  app.get('/hi', function(req, res) {
		res.sendfile('./public/hello.html'); 
	});
  
  app.get('/todo', function(req, res) {
		res.sendfile('./public/todo.html'); 
	});

};

// route middleware

// ensure a user is logged in
function isLoggedIn(req, res, next)
{
  if (req.isAuthenticated())
  {
    // safe to continue
    return next();
  }
  
  // not allowed!
  res.redirect('/');
}

