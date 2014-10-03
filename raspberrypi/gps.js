var serialport = require('./node_modules/serialport');
var nmea = require('./node_modules/nmea');

var port = new serialport.SerialPort('/dev/ttyAMA0', {
                baudrate: 57600,
                parser: serialport.parsers.readline('\r\n')});

console.log('time,lat,latPole,lon,lonPole,numSat');

port.on('data', function(line) {
    var gps = nmea.parse(line);
    
    if (gps.type == 'fix')
    {
      console.log(gps.timestamp + ',' + gps.lat + ',' +  gps.latPole + ',' + gps.lon + ',' + gps.lonPole + ',' + gps.numSat);
    }
    
});
