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


