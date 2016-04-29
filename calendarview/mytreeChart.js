dc.mytreeChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes([]);
  
  var _data, _treeG, _treeData;
  
  var _tree = d3.layout.tree()
    .children(function(d) { return Array.isArray(d.values) ? d.values : []; });
    
  var _nest = d3.nest();
  
  var _diagonal = d3.svg.diagonal().projection(function(d) { return [d.x, d.y]; });
  var _color = d3.scale.category10();
  var _scale = d3.scale.linear().range([0,50]);
  
  _chart.drawTreeNodes = function() {
    
    var nodes = _tree.nodes(_treeData);
    
    var links = _treeG.selectAll('path.link').data(_tree.links(nodes));
    links.exit().remove();
    links.enter().append('path').attr('class', 'link');
    links.transition().attr('d', _diagonal);
    
    var g = _treeG.selectAll('g.node').data(nodes);
    
    g.exit().remove();
    g.enter().append('g').attr('class', 'node')
      .on('click', function() {
        var d = d3.select(this).datum();
        console.log('tree click', d, d3.select(this).attr('class'));
        
        d3.select(this).select('circle').classed('selected', d._selected = !d._selected);
        
        if (!d.parent) {
          //on the root node, reset filters
          catPie.filter(null);
          subcatPie.filter(null);
          
          g.select('circle').classed('selected', function(d) {
            d._selected = false;
            return d._selected; 
          });
        }
        else {
          
          if (d.parent.key == "Root") {
            //apply category filter
            catPie.filter(d.key);
          }
          else {
            // apply category and subcategory filter
            catPie.filter(d.parent.key);
            subcatPie.filter(d.key);
          }
        }
        
        dc.redrawAll();
      });
    g.transition().attr('transform', function(d) { return 'translate('+d.x+','+d.y+')'; });
    
    var c = g.selectAll('circle').data(function(d) { return [d]; });
    c.exit().remove();
    c.enter().append('circle').attr('r', _scale(1));
    c.attr('fill', function(d) { return _color(d.key); })
    c.attr('stroke', function(d) { return _color(d.key); })
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
    
    _treeData = _chart.dataRoot(_nest.entries(_data));
    
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

  _chart.nest = function() {
    return _nest;
  };
  
  _chart.dataRoot = function(entries) {
    return {key: "Root", values: entries};
  };

  return _chart.anchor(parent, chartGroup);
};
