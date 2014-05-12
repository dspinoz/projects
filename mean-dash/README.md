
Getting Started:

npm install
bower install
node server.js



Layout:

- app
----- routes.js
- config
	----- db.js 
- node_modules <!-- created by npm install -->
- public <!-- all frontend and angular stuff -->
----- css
----- js
---------- controllers <!-- angular controllers -->
---------- services <!-- angular services -->
---------- app.js <!-- angular application -->
---------- appRoutes.js <!-- angular routes -->
----- img
----- libs <!-- created by bower install -->
----- views 
---------- home.html
---------- nerd.html
---------- geek.html
----- index.html
- .bowerrc <!-- tells bower where to put files (public/libs) -->
- bower.json <!-- tells bower which files we need -->
- package.json <!-- tells npm which packages we need -->
- server.js <!-- set up our node application -->

- public 
----- lib <!-- third party apps -->
----- js
---------- controllers 
-------------------- MainCtrl.js
-------------------- NerdCtrl.js
-------------------- GeekCtrl.js
---------- services
-------------------- GeekService.js
-------------------- NerdService.js
---------- app.js 
---------- appRoutes.js


Dependencies:
  Express is the web framework.
  Ejs is the templating engine.
  Mongoose is object modeling for our MongoDB database.
  Passport will help us authenticating with different methods.
  Connect-flash allows for passing session flashdata messages.
  Bcrypt-nodejs gives us the ability to hash the password.



Credits
http://scotch.io/bar-talk/setting-up-a-mean-stack-single-page-application 
http://scotch.io/tutorials/javascript/easy-node-authentication-setup-and-local


