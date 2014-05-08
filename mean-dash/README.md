
Getting Started:

npm install
bower install



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



Credits
http://scotch.io/bar-talk/setting-up-a-mean-stack-single-page-application 



