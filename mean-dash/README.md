
Getting Started:

  1. Install dependencies
  
    > npm install
    > bower install

  2. Create a mongo database: mean-dash-dev
    
  3. Verify config/db.js
    
  4. Run 
  
    > node server.js


Development:

  Use nodemon to automatically refresh files: npm install nodemon
  
  > nodemon server.js

Routes:

  /hi -- hello world --
  
  /signup -- passport create user --
  /login  -- passport login --
  /profile -- passport private page --
  /logout --logout --
  
  /todo -- todo app --
  /api/todos -- REST API for todo app --

Layout:

  app
    model -- data models --
      todo.js
      user.js 
    routes.js
  config -- configuration modules --
    db.js  -- database --
    passport.js -- user strategies --
  node_modules -- created by npm install --
  public -- all frontend and angular stuff --
    libs -- created by bower install --
    todo.js -- todo angular --
    hello.html -- hello world --
  views -- templated pages --
    index.ejs  -- home page --
    login.ejs  -- authenticate --
    signup.ejs -- register --
    profile.ejs -- user account view --
  .gitignore -- tells git to ignore generated files --
  .bowerrc -- tells bower where to put files (public/libs) --
  bower.json -- tells bower which packages we need --
  package.json -- tells npm which packages we need --
  server.js -- bootstrap - set up our node application --


Dependencies:
  Express is the web framework.
  Ejs is the templating engine.
  Mongoose is object modeling for our MongoDB database.
  Passport will help us authenticating with different methods.
  Connect-flash allows for passing session flashdata messages.
  Bcrypt-nodejs gives us the ability to hash the password.



Credits
http://scotch.io/tutorials/javascript/easy-node-authentication-setup-and-local
http://scotch.io/tutorials/javascript/creating-a-single-page-todo-app-with-node-and-angular

