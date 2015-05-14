var fs = require('fs');
var zlib = require('zlib');
var fspath = require('path');

module.exports.types = ['application/x-gzip'];

module.exports.matches_buff = function(buff) {};

module.exports.matches_file = function(path) {};

module.exports.process_buff = function(job,buff,queue,done) {};

module.exports.process_file = function(job,path,add_buff,add_file,done) {
  
  var buf = fs.readFile(path, function(fserr, buf) {
    if (fserr) done(fserr, null);
    
    zlib.gunzip(buf, function(err,res) {
      if (err) done(err, null);
      
      var name = fspath.basename(path);
      var groups = undefined;
      
      console.log("GUNZIP", name, name.match(/(.*)\.(gz|tar)$/));
      
      if ((groups = name.match(/(.*)\.gz$/)) != null)
      {
        name = groups[1];
      }
      
      add_buff(res, name, {parent: job.id});
      
      done(null,{zlib: 'gunzip'});
    });
  });
};
