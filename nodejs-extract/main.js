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
var job_priority = 'normal';
var subjob_priority = 'medium'; //get done first

// globals
var queue = kue.createQueue();
var magic = new mmm.Magic(mmm.MAGIC_MIME_TYPE);

var queue_buff = function(buf, name, info, priority) {
  var job = queue.create('extract-file', {
              title: 'Add buffer' + (name ? ' ' + name : ''),
              buffer: buf.toString('base64'),
              name: name,
              info: info
            })
            .priority(!priority ? subjob_priority : priority) 
            .attempts(1) // before being marked as failure
            //.ttl(60000) // milliseconds for maximum time in active state
            .delay(0) // milliseconds for when job should be executed
            .save();
  
  return job;
};

var queue_file = function(fpath, priority) {
  var job = queue.create('extract-file', {
              title: 'Add file' + (fpath ? ' ' + path.basename(fpath) : ''),
              path: fpath
            })
            .priority(!priority ? subjob_priority : priority) //get subjobs done first
            .attempts(1) // before being marked as failure
            //.ttl(60000) // milliseconds for maximum time in active state
            .delay(0) // milliseconds for when job should be executed
            .save();
  
  return job;
};

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
      console.log('Job %d complete (type %s)', id, job.type, job.result);
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
      queue_file(real, 'normal');
    });
  });
}
else
{
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
      var types = [];
      
      if (lib.types)
      {
        types = lib.types;
        console.log("Loading", path.basename(real), types);
      }
      else
      {
        types = ['*'];
        console.log("Loading", path.basename(real));
      }
      
      lib.name = path.basename(real);
      
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
  
  // workers process one job at a time
  queue.process('extract-file', function(job, done) {
    
    var err = null;
    var result = {};
    console.log('Extract-file Job %d processing: %s', job.id, job.data.path ? job.data.path : 'buffer ('+job.data.buffer.length+' bytes)', job.data.info ? job.data.info : null);
    
    if (job.data.path)
    {
      magic.detectFile(job.data.path, function(err, result) {
        if (err) throw err;
        console.log('%s is %s %s', path.basename(job.data.path), result, libs[result] == undefined ? "NO":"YES");
        
        var processed = false;
        if (libs[result])
        {
          for(var i = 0; i < libs[result].length; i++)
          {
            var lib = libs[result][i];
            lib.process_file(job, job.data.path, queue_buff, queue_file, done);
          }
        }
        else
        {
          done(null, {type: result, processed: false});
        }
      });
    }
    else if (job.data.buffer)
    {
      var buf = new Buffer(job.data.buffer, 'base64');
      magic.detect(buf, function(err, result) {
        console.log('buffer %s is %s %s', job.data.name ? job.data.name : 'UNKNOWN', result, libs[result] == undefined ? "NO":"YES");
        done(err,result);
      });
    }
  });
}






