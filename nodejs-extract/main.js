#!/usr/bin/env node
// standard modules
var util = require('util');
var path = require('path');
var fs = require('fs');

// non-standard modules
var cluster = require('cluster');
var kue = require('kue');

//configuration
var kue_port = 3000;
var workers = require('os').cpus().length;

// globals
var queue = kue.createQueue();

if (cluster.isMaster) 
{
  //main thread
  kue.app.listen(kue_port);
  console.log('Kue listening on port', kue_port);
  
  console.log('Spawning', workers, 'workers with cluster');
  for (var i = 0; i < workers; i++) 
  {
    cluster.fork();
  }
  
  // generic queue events
  queue.on('job enqueue', function(id, type){
    console.log( 'Job %d got queued (type %s)', id, type );
  }).on('job complete', function(id, result){
    kue.Job.get(id, function(err, job){
      console.log('Job %d complete (type %s)', id, job.type);
      if (err) return;
      job.remove(function(err){
        if (err) throw err;
        console.log('Job %d removed', job.id);
      });
    });
  });
  
  // create some example jobs
  
  fs.readdir('./test', function(err, files) {
    files.forEach(function(f) {
      var real = fs.realpathSync(util.format('./test/%s', f));
      queue.create('extract-file', {
        title: util.format('%s', path.basename(real)),  //special-cased for UI
        path: real
      })
      .priority('normal') //low, normal, medium, high, critical
      .attempts(1) // before being marked as failure
      .ttl(60000) // milliseconds for maximum time in active state
      .delay(0) // milliseconds for when job should be executed
      .save();
    });
  });
}
else
{
  // workers process one job at a time
  queue.process('extract-file', function(job, done) {
    
    var err = null;
    var result = {};
    console.log('Extract-file Job %d processing: %s', job.id, job.data.path);
    
    var high = 10;
    var low = 1;
    var rand = Math.floor(Math.random() * (high - low + 1) + low)*1000;
    console.log('Job %d %d', job.id, rand);
    
    setTimeout(done, rand);
  });
}






