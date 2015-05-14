#!/usr/bin/env node
// standard modules
var util = require('util');
var path = require('path');
var fs = require('fs');
var cluster = require('cluster');

// non-standard modules
var kue = require('kue');
var mmm = require('mmmagic');

//configuration
var kue_port = 3000;
var workers = require('os').cpus().length;

// globals
var queue = kue.createQueue();
var magic = new mmm.Magic(mmm.MAGIC_MIME_TYPE);
var libs = {};
var libs_loaded = 0;

// load extraction libraries
var files = fs.readdirSync('./lib');
files.forEach(function(f) {
  var real = fs.realpathSync(util.format('./lib/%s', f));
  if (!real.match(/(.*)\.js$/))
  {
    return;
  }
  
  var lib = require(real);
  if ((lib.types || (lib.matches_buff && lib.matches_file)) &&
      (lib.process_buff && lib.process_file))
  {
    console.log("Loading", path.basename(real));
    var types = []
    if (lib.types)
    {
      types = lib.types;
    }
    else
    {
      types = ['*'];
    }
    
    types.forEach(function (t) {
      if (!libs[t]) libs[t] = [];
      libs[t].push(lib);
    });
    
    libs_loaded++;
  }
  else
  {
    console.log("ERROR Invalid library", path.basename(real));
  }
});

if (libs_loaded <= 0)
{
  console.log("ERROR No libraries loaded");
  process.exit(1);
}

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
      console.log('%s is %s %s', path.basename(job.data.path), result, libs[result] == undefined ? "NO":"YES");
      
      if (libs[result])
      {
        for(var i = 0; i < libs[result].length; i++)
        {
          var lib = libs[result][i];
          if (job.data.path && 
              lib.process_file(job.data.path, queue, done))
          {
            break;
          }
        }
      }
    });
  });
}






