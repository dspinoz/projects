#!/usr/bin/env node
var cluster = require('cluster');
var kue = require('kue');
var queue = kue.createQueue();

//configuration
var kue_port = 3000;
var workers = require('os').cpus().length;

if (cluster.isMaster) 
{
  //main thread
  kue.app.listen(kue_port);
  console.log('kue port', kue_port);
  
  console.log('Spawning', workers, 'workers with cluster');
  for (var i = 0; i < workers; i++) 
  {
    cluster.fork();
  }
  
  queue.on('job enqueue', function(id, type){
    console.log( 'Job %s got queued of type %s', id, type );
  }).on('job complete', function(id, result){
    kue.Job.get(id, function(err, job){
      if (err) return;
      job.remove(function(err){
        if (err) throw err;
        console.log('removed completed job #%d', job.id);
      });
    });
  });
  
  for (var i = 0; i < 5; i++)
  {
    var job = queue.create('email', {
        title: 'welcome email for tj',  //special-cased for UI
        to: 'tj@learnboost.com',
        template: 'welcome-email'
      })
      .priority('high') //low, normal, medium, high, critical
      .attempts(1) // before being marked as failure
      .ttl(60000) // milliseconds for maximum time in active state
      .delay(0) // milliseconds for when job should be executed
      .save();
  }
  console.log('sent for processing');
}
else
{
  // workers process one job at a time
  queue.process('email', function(job, done) {
    
    var err = null;
    var result = {};
    console.log('Processing job from queue', job.type, job.data);
    job.log('Job', job.id, 'processing');
    
    done(err, result);
    console.log('done', job.id);
  });
}






