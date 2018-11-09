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
var columns = 3;

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
  
  var w = 3;
  var rect = d3.select('#h-scrollbar').selectAll('rect').data(pdata);
  rect.exit().remove();
  rect.enter()
    .append('rect')
    .merge(rect)
    .attr('x',function(d,i){ return i*w; })
    .attr('y',0)
    .attr('width',w)
    .attr('height',w)
    .style('fill',function(d,i){
      if (i >= pstart && i < pend) return 'black';
      return 'white';
    });
  
  
  var p = d3.select('#photos').selectAll('p').data(pdata.filter(function(d,i){ return i >= pstart && i < pend; }));
  p.exit().remove();
  p.enter()
    .append('p')
    .merge(p)
    .text(function(d){ return d; });
}

updateP();

