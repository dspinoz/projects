'use strict';

// The Package is past automatically as first parameter
module.exports = function(Polls, app, auth, database) {

    app.get('/polls/example/anyone', function(req, res, next) {
        res.send('Anyone can access this');
    });

    app.get('/polls/example/auth', auth.requiresLogin, function(req, res, next) {
        res.send('Only authenticated users can access this');
    });

    app.get('/polls/example/admin', auth.requiresAdmin, function(req, res, next) {
        res.send('Only users with Admin role can access this');
    });

    app.get('/polls/example/render', function(req, res, next) {
        Polls.render('index', {
            package: 'polls'
        }, function(err, html) {
            //Rendering a view from the Package server/views
            res.send(html);
        });
    });
};
