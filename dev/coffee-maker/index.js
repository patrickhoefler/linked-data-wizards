var chokidar = require('chokidar');
var exec = require('child_process').exec;

var watcher = chokidar.watch(
  '/vagrant/ldva/apps/querywizard/static/js/querywizard.coffee',
  {
    interval: 1000,
    usePolling: true
  }
);

watcher
  .on('change', function(path, stats) {
    outputPath = path.split("/").slice(0, -1).join("/");
    command = 'coffee --compile --output ' + outputPath + ' ' + path;
    exec(command, function callback(error, stdout, stderr) {
      console.log(new Date().toISOString() + " " + command);
    });
  })
