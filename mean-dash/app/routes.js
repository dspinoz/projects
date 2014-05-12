module.exports = function(app, passport) {

  // server routes ===========================================================
  // handle things like api calls
  // authentication routes
  
  // home page with login links
  app.get('/', function(req, res) {
    res.render('index.ejs');
  });
  
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

