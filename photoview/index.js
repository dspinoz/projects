var facts = crossfilter();
var picset = d3.set();

var charts = {
  itemCount: dc.numberDisplay("#chart-count"),
  make: dc.pieChart("#chart-make"),
  model: dc.pieChart("#chart-model"),
  exposureMode: dc.pieChart("#chart-exposure-mode"),
  exposureProgram: dc.pieChart("#chart-exposure-program"),
  aperture: dc.pieChart("#chart-aperture"),
  flash: dc.pieChart("#chart-flash"),
  lens: dc.pieChart("#chart-lens"),
  whiteBalance: dc.pieChart("#chart-white-balance"),
  focalLength: dc.pieChart("#chart-focal-length"),
  focusMode: dc.pieChart("#chart-focus-mode"),
  fileType: dc.pieChart("#chart-file-type")
}

var dimensions = {
  id: facts.dimension(function(d,i) {return i; }),
  make: facts.dimension(function(d){ return d['Make']; }),
  model: facts.dimension(function(d){ return d['Model']; }),
  exposureMode: facts.dimension(function(d){ return d['ExposureMode']; }),
  exposureProgram: facts.dimension(function(d){ return d['ExposureProgram']; }),
  aperture: facts.dimension(function(d){ return d['Aperture']; }),
  flash: facts.dimension(function(d){ return d['Flash']; }),
  lens: facts.dimension(function(d){ return d['Lens']; }),
  whiteBalance: facts.dimension(function(d){ return d['WhiteBalance']; }),
  focalLength: facts.dimension(function(d){ return d['FocalLength']; }),
  focusMode: facts.dimension(function(d){ return d['FocusMode']; }),
  fileType: facts.dimension(function(d){ return d['FileType']; })
}

charts.itemCount
  .formatNumber(Math.round)
  .group(facts.groupAll().reduceCount())
  .valueAccessor(function(d) { return d; });
  
charts.make
  .dimension(dimensions.make)
  .group(dimensions.make.group().reduceCount());
  
charts.model
  .dimension(dimensions.model)
  .group(dimensions.model.group().reduceCount());
  
charts.exposureMode
  .dimension(dimensions.exposureMode)
  .group(dimensions.exposureMode.group().reduceCount());
  
charts.exposureProgram
  .dimension(dimensions.exposureProgram)
  .group(dimensions.exposureProgram.group().reduceCount());
  
charts.aperture
  .dimension(dimensions.aperture)
  .group(dimensions.aperture.group().reduceCount());
  
charts.flash
  .dimension(dimensions.flash)
  .group(dimensions.flash.group().reduceCount());
  
charts.lens
  .dimension(dimensions.lens)
  .group(dimensions.lens.group().reduceCount());
  
charts.whiteBalance
  .dimension(dimensions.whiteBalance)
  .group(dimensions.whiteBalance.group().reduceCount());
  
charts.focalLength
  .dimension(dimensions.focalLength)
  .group(dimensions.focalLength.group().reduceCount());
  
charts.focusMode
  .dimension(dimensions.focusMode)
  .group(dimensions.focusMode.group().reduceCount());
  
charts.fileType
  .dimension(dimensions.fileType)
  .group(dimensions.fileType.group().reduceCount());

dc.renderAll();

var pdata = d3.range(0,104);
var pstart = 0, pend = 30;
var columns = 3;

d3.select('#photos').text('photos here..')
.on('mousewheel', function() {
  d3.event.preventDefault();
  var shift = columns;
  if (d3.event.wheelDelta > 0) shift = -1*columns;
  
  console.log('hello scroll',d3.event.wheelDelta < 0 ? 'down' : 'up',d3.event.wheelDelta,shift,pstart,pstart+shift,pend,pend+shift);
  
  
  while (pstart + shift < 0) shift++;
  while (pend + shift > pdata.length) shift--;
  
  pstart += shift;
  pend += shift;
  updateP();
  
})
.on('click', function() {
  console.log('hello');
});

function updateP() {
  
  pdata.filter(function(d,i){ return i >= pstart && i < pend; }).forEach(function(p) {
    if (!picset.has(p)) {
      d3.json('/exif/'+p).then(function(data) {
        picset.add(p);
        facts.add(data);
        dc.redrawAll();
      });
    }
  });
  
  var xScale = d3.scaleBand().range([0,1000]).domain(pdata).paddingInner(0.01);
  var rect = d3.select('#h-scrollbar').selectAll('rect').data(pdata);
  rect.exit().remove();
  rect.enter()
    .append('rect')
    .merge(rect)
    .attr('x',function(d,i){ return i*xScale.bandwidth(); })
    .attr('y',0)
    .attr('width',xScale.bandwidth())
    .attr('height',10)
    .style('fill',function(d,i){
      if (i >= pstart && i < pend) return 'black';
      return '#ccc';
    });
  
  var rows = [];
  var current = [];
  
  pdata.filter(function(d,i){ return i >= pstart && i < pend; }).forEach(function(d) {
    if (current.length>=columns) {
      rows.push(current);
      current = [];
    }
    current.push(d);
  });
  if (current.length){
    rows.push(current);
    current = null;
  }
  
  var row = d3.select('#photos').selectAll('div.row').data(rows);
  row.exit().remove();
  row = row.enter()
    .append('div')
    .classed('row',true)
    .merge(row);
    
  var img = row.selectAll('img').data(function(d){ return d; });
  img.exit().remove();
  img.enter()
    .append('img')
    .merge(img)
    .attr('src',function(d){ return '/icons/'+d; });
}

updateP();
