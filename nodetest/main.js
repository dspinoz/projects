var fs = require('fs-extra');

var json = fs.readJson("./package.json", function(err, obj) {
  if (err) return console.error(err);
  console.log(obj);
});

console.log("done");