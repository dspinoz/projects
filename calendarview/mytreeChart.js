dc.mytreeChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension']);
  
  _chart.colorAccessor(function(d) { return d.key; });
  
  var _treeG;
  
  var _tree = d3.layout.tree()
    .children(function(d) { return Array.isArray(d.values) ? d.values : []; });
    
  var _nest = d3.nest();
  var _title = function(d) { return d; };
  var _filterFunc = function(d) { return d; };
  
  var _diagonal = d3.svg.diagonal().projection(function(d) { return [d.x, d.y]; });
  var _scale = d3.scale.linear().range([0,50]);
  
  _chart.drawTreeNodes = function() {
    
    // new data is regenerated every refresh - not persistent!!
    var treeData = _chart.dataRoot(_nest.entries(_chart.dimension().top(Infinity)));
    
    var nodes = _tree.nodes(treeData);
    
    var links = _treeG.selectAll('path.link').data(_tree.links(nodes));
    links.exit().remove();
    links.enter().append('path').attr('class', 'link');
    links.transition().attr('d', _diagonal);
    
    var g = _treeG.selectAll('g.node').data(nodes);
    
    g.exit().remove();
    g.enter().append('g').attr('class', 'node')
      .on('click', function() {
        // TBD save state for what item is selected and maintain selection as data changes
        
        var d = d3.select(this).datum();
        
        _chart.filter(_filterFunc(d));
        
        dc.redrawAll();
      });
      
    g.transition().attr('transform', function(d) { return 'translate('+d.x+','+d.y+')'; });
    
    var t = g.selectAll('title').data(function(d) { return [d]; });
    t.exit().remove();
    t.enter().append('title');
    t.text(_chart.title());
    
    var c = g.selectAll('circle').data(function(d) { return [d]; });
    c.exit().remove();
    c.enter().append('circle').attr('r', _scale(1));
    c
      .attr('fill', _chart.getColor)
      .attr('stroke', _chart.getColor)
      .attr('r', function(d) { 
        if (Array.isArray(d.values)) {
          return _scale(1); 
        }
        return _scale(d.values);
      });
  };
  
  _chart._doRender = function () {
    _chart.resetSvg();
    console.log('mytree render');
    
    var width = _chart.width() - _chart.margins().right - _chart.margins().left,
        height = _chart.height() - _chart.margins().top - _chart.margins().bottom;

    _tree.size([width, height]);

    _treeG = _chart.svg()
        .attr("width", width + _chart.margins().right + _chart.margins().left)
        .attr("height", height + _chart.margins().top + _chart.margins().bottom)
      .append("g")
        .attr("transform", "translate(" + _chart.margins().left + "," + _chart.margins().top + ")");
    
    _chart.drawTreeNodes();
    
    return _chart;
  };

  _chart._doRedraw = function () {
    console.log('mytree redraw');
    
    _chart.drawTreeNodes();
    
    return _chart;
  };

  _chart.data = function (data) {
    if (!arguments.length) {
      return _data;
    }
    _data = data;
    return _chart;
  };

  _chart.scale = function (scale) {
    if (!arguments.length) {
      return _scale;
    }
    _scale = scale;
    return _chart;
  };
  
  _chart.treeChildren = function (f) {
    if (!arguments.length) {
      return _tree.children();
    }
    _tree.children(f);
    return _chart;
  };
  
  _chart.title = function (f) {
    if (!arguments.length) {
      return _title;
    }
    _title = f;
    return _chart;
  };

  _chart.filterFunc = function (f) {
    if (!arguments.length) {
      return _filterFunc;
    }
    _filterFunc = f;
    return _chart;
  };

  _chart.nest = function() {
    return _nest;
  };
  
  _chart.dataRoot = function(entries) {
    return {key: "Root", values: entries};
  };

  return _chart.anchor(parent, chartGroup);
};
