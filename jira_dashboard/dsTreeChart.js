dc.dsTreeChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension']);
  
  _chart.colorAccessor(function(d) { return d.key; });
  
  var _treeG;
  
  var _nest = d3.nest();
  var _title = function(d) { return _key(d); };
  var _filterFunc = function(d) { return _key(d); };
  var _projection = function(d) { return [d.x, d.y]; };
  var _children = function(d) { return Array.isArray(d.values) ? d.values : undefined; };
  var _key = function(d) { return d.key; };
  var _value = function(d) { 
    if (Array.isArray(d.values)) {
      return 1; 
    }
    return d.values;
  };
  var _renderNode = function(selection) {
    var c = selection.selectAll('circle').data(function(d) { return [d]; });
    c.exit().remove();
    c.enter().append('circle').attr('r', _scale(1));
    c
      .attr('fill', _chart.getColor)
      .attr('stroke', _chart.getColor)
      .attr('r', function(d) {
        return _scale(_value(d));
      });
  };
  var _extent = function(d) {
    return _value(d);
  };
  
  var _tree = d3.layout.tree().children(_children);
  var _diagonal = d3.svg.diagonal().projection(_projection);
  var _scale = d3.scale.linear().range([5,30]);
  
  _chart.drawTreeNodes = function() {
    
    // new data is regenerated every refresh - not persistent!!
    var data = _nest.entries(_chart.dimension().top(Infinity));
    
    var treeData = _chart.dataRoot(data);
    
    
    // flattens the hierarchial data structure
    // sort nodes to ensure that bigger nodes are drawn first
    // TBD collision detection and move nodes within the tree structure
    
    var nodes = _tree.nodes(treeData).sort(function(a,b) {
      return d3.descending(_value(a), _value(b));
    });
    
    _scale.domain(d3.extent(nodes, _extent));
    
    
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
    
    _renderNode(g);
  };
  
  _chart._doRender = function () {
    _chart.resetSvg();
    
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
    
    _chart.drawTreeNodes();
    
    return _chart;
  };

  _chart.children = function (f) {
    if (!arguments.length) {
      return _children;
    }
    _children = f;
    return _chart;
  };

  _chart.projection = function (f) {
    if (!arguments.length) {
      return _projection;
    }
    _projection = f;
    return _chart;
  };

  _chart.key = function (f) {
    if (!arguments.length) {
      return _key;
    }
    _key = f;
    return _chart;
  };
  
  _chart.value = function (f) {
    if (!arguments.length) {
      return _value;
    }
    _value = f;
    return _chart;
  };
  
  _chart.scale = function (scale) {
    if (!arguments.length) {
      return _scale;
    }
    _scale = scale;
    return _chart;
  };
  
  _chart.extent = function (f) {
    if (!arguments.length) {
      return _extent;
    }
    _extent = f;
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
  
  _chart.renderNode = function (f) {
    if (!arguments.length) {
      return _renderNode;
    }
    _renderNode = f;
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
