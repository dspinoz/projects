#!/usr/bin/env node
// standard modules
var util = require('util');
var path = require('path');
var fs = require('fs');
var cluster = require('cluster');

// non-standard modules
var kue = require('kue');
var mmm = require('mmmagic'), Magic = mmm.Magic;
var magic = new Magic(mmm.MAGIC_MIME_TYPE | mmm.MAGIC_MIME_ENCODING);

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
    
    magic.detectFile(job.data.path, function(err, result) {
      if (err) throw err;
      console.log('%s is %s', path.basename(job.data.path), result);
      done(null, result);
    });
      
    
  });
}






