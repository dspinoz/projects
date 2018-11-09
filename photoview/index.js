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

var pdata = d3.range(0,104);
var pstart = 0, pend = 30;
var columns = 3;

d3.select('#photos').text('photos here..')
.on('mousewheel', function() {
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
    
  var p = row.selectAll('p').data(function(d){ return d; });
  p.exit().remove();
  p.enter()
    .append('p')
    .merge(p)
    .html(function(d){ return d+"&nbsp;&nbsp;"; });
}

updateP();

