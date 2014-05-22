
# Getting Started
1. Install dependencies

> ```
npm install
bower install
```

2. Create a mongo database ```mean-dash-dev```
3. Configure ```config/db.js```
4. Run

> ```
node server.js
```

# Development tips

1. Automatically run and refresh files

> ```
npm install nodemon
nodemon server.js
```


# Routes

#### Example 

| URI |  Description |
| ------- | ------------ |
| /hi | hello world |

#### Passport

| URI |  Description |
| ------- | ------------ |
| /signup | passport create user |
| /login | passport login |
| /profile | passport private page |
| /logout | passport logout |

#### Todo

| Method | URI | Description |
| ------ | --- | ----------- |
| GET | /todo | Create a list of items and delete them once they are complete |
| GET | /api/todos | List all the todos in the database |
| POST | /api/todos | Create a new todo | 
| DELETE | /api/todos/:todo_id | Delete a todo |

#### Polls

| Method | URI | Description |
| ------ | --- | ----------- |
| GET | /polls | Application for recording polls and the choices users' make |
| GET | /polls/polls | Get the list of polls |
| POST | /polls/polls | Create new Poll |
| GET | /polls/:id | Get details for a particular poll |

| WebSocket | Description |
| --------- | ----------- |
| send:vote | Record a vote for a poll |
| emit:myvote | Notify the voting client of a vote |
| emit:broadcast:vote | Notify other clients of a vote |

# Layout

<ul>
  <li><code>app/</code> Application definition files</li>
  <ul>
    <li><code>model/</code> Data models</li>
    <ul>
      <li><code>todo.js</code></li>
      <li><code>user.js</code></li>
      <li><code>poll.js</code></li>
    </ul>
  </ul>
  <ul>
    <li><code>routes.js</code></li>
  </ul>
  <li><code>config/</code> Configuration modules</li>
  <ul>
    <li><code>db.js</code> Database</li>
    <li><code>passport.js</code> Login strategies</li>
  </ul>
  <li><code>node_modules/</code> Created by install</li>
  <li><code>public/</code> Static files available on the web server</li>
  <ul>
    <li><code>libs/</code> Created by install</li>
    <li><code>js/</code> Custom javascript</li>
    <ul>
      <li><code>services/</code> Angular services</li>
      <ul>
        <li><code>todo.js</code> Todo Angular service</li>
        <li><code>polls.js</code> Polls Angular service</li>
      </ul>
      <li><code>controllers/</code> Angular controllers</li>
      <ul>
        <li><code>todo.js</code> Todo Angular controller</li>
        <li><code>polls.js</code> Polls Angular controller</li>
      </ul>
      <li><code>todo.js</code> Todo application routes</li>
      <li><code>polls.js</code> Polls application routes</li>
    </ul>
    <ul>
      <li><code>polls/</code> Polls-specific pages</li>
      <ul>
        <li><code>new.html</code> Angular template for creating a new poll</li>
        <li><code>item.html</code> Angular template for poll item</li>
        <li><code>list</code> Angular template for listing polls</li>
      </ul>
    </ul>
    <li><code>hello.html</code> Hello world page</li>
    <li><code>todo.html</code> Todo front-end</li>
    <li><code>polls.html</code> Polls front-end</li>
  </ul>
  <li><code>views/</code> Templated pages</li>
  <ul>
    <li><code>index.ejs</code> Home page for user login</li>
    <li><code>login.ejs</code> User authentication</li>
    <li><code>signup.ejs</code> User registration</li>
    <li><code>profile.ejs</code> User account view</li>
  </ul>
  <li><code>.bowerrc</code> Tells bower where to put files <code>public/libs</code></li>
  <li><code>.gitignore</code> Tells git which files to ignore</li>
  <li><code>bower.json</code> Tells bower our dependencies</li>
  <li><code>server.js</code> Bootstrap and setup the application</li>
  <li><code>package.json</code> Tells npm our dependencies</li>
</ul>


# Dependencies
* Express is the web framework.
* Ejs is the templating engine.
* Mongoose is object modeling for our MongoDB database.
* Passport will help us authenticating with different methods.
* Connect-flash allows for passing session flashdata messages.
* Bcrypt-nodejs gives us the ability to hash the password.

# Credits
* http://scotch.io/tutorials/javascript/easy-node-authentication-setup-and-local
* http://scotch.io/tutorials/javascript/creating-a-single-page-todo-app-with-node-and-angular
* http://www.ibm.com/developerworks/library/wa-nodejs-polling-app/
