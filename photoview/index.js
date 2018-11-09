var facts = crossfilter();

var charts = {
  itemCount: dc.numberDisplay("#chart-count")
}

var dimensions = {
  id: facts.dimension(function(d,i) {return i; })
}

charts.itemCount
  .formatNumber(Math.round)
  .group(facts.groupAll().reduceCount())
  .valueAccessor(function(d) { return d; });

dc.renderAll();

var pdata = d3.range(0,100);
var pstart = 0, pend = 10;

d3.select('#photos').text('photos here..')
.on('mousewheel', function() {
  var shift = 1;
  if (d3.event.wheelDelta > 0) shift = -1;
  
  console.log('hello scroll',d3.event.wheelDelta < 0 ? 'down' : 'up',d3.event.wheelDelta,shift,pstart,pstart+shift,pend,pend+shift);
  
  
  if (pstart + shift < 0) return;
  if (pend + shift > (pdata.length-1)) return;
  
  pstart += shift;
  pend += shift;
  updateP();
  
})
.on('click', function() {
  console.log('hello');
});

function updateP() {
  var p = d3.select('#photos').selectAll('p').data(pdata.filter(function(d,i){ return i >= pstart && i < pend; }));
  p.exit().remove();
  p.enter()
    .append('p')
    .merge(p)
    .text(function(d){ return d; });
}

updateP();

