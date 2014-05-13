// models
var Todo = require('./models/todo');
var Poll = require('./models/poll');

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
  
  app.get('/polls', function(req, res) {
    res.sendfile('./public/polls.html');
  });
  
  // ============================POLLS===============================
  
  // get a list of polls
  app.get('/polls/polls', function(req, res) { 
    Poll.find({}, 'question', function(error, polls) {
      res.json(polls);
    });
  });
  
  // get a single poll
  app.get('/polls/:id', function(req, res) {  
    var pollId = req.params.id;
    Poll.findById(pollId, '', { lean: true }, function(err, poll) {
      if(poll) {
        var userVoted = false,
            userChoice,
            totalVotes = 0;
        for(c in poll.choices) {
          var choice = poll.choices[c]; 
          for(v in choice.votes) {
            var vote = choice.votes[v];
            totalVotes++;
            if(vote.ip === (req.header('x-forwarded-for') || req.ip)) {
              userVoted = true;
              userChoice = { _id: choice._id, text: choice.text };
            }
          }
        }
        poll.userVoted = userVoted;
        poll.userChoice = userChoice;
        poll.totalVotes = totalVotes;
        res.json(poll);
      } else {
        res.json({error:true});
      }
    });
  });
  
  app.post('/polls', function(req, res) {
    var reqBody = req.body,
        choices = reqBody.choices.filter(function(v) { return v.text != ''; }),
        pollObj = {question: reqBody.question, choices: choices};
    var poll = new Poll(pollObj);
    poll.save(function(err, doc) {
      if(err || !doc) {
        throw 'Error';
      } else {
        res.json(doc);
      }   
    });
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

