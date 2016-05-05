
dc.myDimensions = function(parent, chartGroup) {
  var _chart = dc.baseMixin({});
  
  _chart._mandatoryAttributes([])
    .anchor(parent, chartGroup);
    
  var _dimensions = [];
  var _count = 0;
  
  _chart._doRender = function () {
    
    _chart._doRedraw();
    
    return _chart;
  };
  
  _chart._doRedraw = function () {
    
    var div = _chart.selectAll('div').data(_dimensions);
    
    div.exit().remove();
    
    div.enter()
      .append('div');
      
    div.text(function(d) {
      var crossfilter = d.cf, 
          txt = d.func;
          
      var top = crossfilter.top(Infinity);
      
      var out = '';
      top.forEach(function(d) {
        var t = txt(d);
        
        if (t) {
          out += t + ',';
        }
      });
      
      return (_count++) + ": "+ out;
    });
    
    return _chart;
  };
  
  _chart.dimension = function (d, f) {
    if (!arguments.length) {
      return _dimensions;
    }
    _dimensions.push({cf: d, func: f});
    return _chart;
  };
  
  return _chart;
};
