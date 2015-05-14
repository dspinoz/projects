module.exports.types = ['application/x-gzip'];

module.exports.matches_buff = function(buff) {
  
};

module.exports.matches_file = function(path) {
  
};

module.exports.process_buff = function(buff,queue,done) {
  
};

module.exports.process_file = function(path,queue,done) {
  
  console.log("gunzip processing");
  done(null,'gunzip done');
};
