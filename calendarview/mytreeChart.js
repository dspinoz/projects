dc.mytreeChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  var _data, _max;
  
  var _tree = d3.layout.tree();
  
  var _diagonal = d3.svg.diagonal().projection(function(d) { return [d.x, d.y]; });
  var _color = d3.scale.category10();
  var _scale = d3.scale.linear();
  
  _chart._doRender = function () {
    _chart.resetSvg();
    console.log('mytree render');
    
    var margin = {top: 10, right: 20, bottom: 20, left: 20},
        _width = _chart.width() - margin.right - margin.left,
        _height = _chart.height() - margin.top - margin.bottom;

    _tree.size([_width, _height]);

    var catTree = _chart.svg()
        .attr("width", _width + margin.right + margin.left)
        .attr("height", _height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      
    _scale.domain([0,_max]).range([2,30]);
    
    var nodes = _tree.nodes(_data);
    
    var links = catTree.selectAll('path.link').data(_tree.links(nodes));
    links.exit().remove();
    links.enter().append('path').attr('class', 'link');
    links.transition().attr('d', _diagonal);
    
    var g = catTree.selectAll('g.node').data(nodes);
    
    g.exit().remove();
    g.enter().append('g').attr('class', 'node')
      .on('click', function() {
        var d = d3.select(this).datum();
        console.log('tree click', d);
        
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
    
    
    return _chart;
  };

  _chart._doRedraw = function () {
    console.log('mytree redraw');
    return _chart;
  };

  _chart.data = function (data) {
    if (!arguments.length) {
      return _data;
    }
    _data = data;
    return _chart;
  };
  
  _chart.max = function (max) {
    if (!arguments.length) {
      return _max;
    }
    _max = max;
    return _chart;
  };

  _chart.treeChildren = function (f) {
    if (!arguments.length) {
      return _tree.children();
    }
    _tree.children(f);
    return _chart;
  };

  return _chart.anchor(parent, chartGroup);
};
