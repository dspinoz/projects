var serialport = require('./node_modules/serialport');
var nmea = require('./node_modules/nmea');

var port = new serialport.SerialPort('/dev/ttyAMA0', {
                baudrate: 57600,
                parser: serialport.parsers.readline('\r\n')});

port.on('data', function(line) {
    console.log(nmea.parse(line));
});
