var fs = require('fs');
var zlib = require('zlib');

module.exports.types = ['application/x-gzip'];

module.exports.matches_buff = function(buff) {
  
};

module.exports.matches_file = function(path) {
  
};

module.exports.process_buff = function(job,buff,queue,done) {
  
};

module.exports.process_file = function(job,path,queue,done) {
  
  var buf = fs.readFile(path, function(fserr, buf) {
    if (fserr) done(fserr, null);
    
    zlib.gunzip(buf, function(err,res) {
      if (err) done(err, null);
      
      console.log('gunzip', res);
      
      queue.create('extract-file', {
        title: 'gunzipped',
        buffer: res.toString('base64')
      })
      .priority('normal') //low, normal, medium, high, critical
      .attempts(1) // before being marked as failure
      .ttl(60000) // milliseconds for maximum time in active state
      .delay(0) // milliseconds for when job should be executed
      .save();
      
      done();
    });
  });
  
};
