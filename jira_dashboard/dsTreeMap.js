dc.dsTreeMap = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension']);
  
  _chart.colorAccessor(function(d) { return d.key; });
  
  var _treeG;
  
  var _nest = d3.nest();
  var _title = function(d) { return _key(d); };
  var _filterFunc = function(d) { return _key(d); };
  var _projection = function(d) { return [d.x, d.y]; };
  //var _children = function(d) { return Array.isArray(d.values) ? d.values : undefined; };
  
  var _children = function(d) { return Array.isArray(d.values) ? d.values : null; };
  var _value = function(d) { 
      console.log(d.key,d.values,Array.isArray(d.values),'=',Array.isArray(d.values) ? 0 : d.values);
      return Array.isArray(d.values) ? 0 : d.values; 
    };
  
  
  
  var _key = function(d) { return d.key; };
  /*var _value = function(d) { 
  console.log('vvv',d);
    if (Array.isArray(d.values)) {
      return 1; 
    }
    return d.values;
  };*/
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
  
  var _tree = d3.layout.treemap().children(_children).round(true).sticky(false).value(_value);
  var _diagonal = d3.svg.diagonal().projection(_projection);
  var _scale = d3.scale.linear().range([5,30]);
  
  function printSel(sel,msg) {
    d3.select(sel).each(function(d,i) {
      console.log(msg,i,this,d);
    });
  }
  
  _chart.drawTreeNodes = function() {
    
    // new data is regenerated every refresh - not persistent!!
    var raw = _chart.dimension().top(Infinity);
    
    if (raw.length == 0) return;
    
    var data = _nest.entries(raw);
    
    
    //data = {"name":"Root",values:data};
    
    var treeData = _chart.dataRoot(data);
    
    
    // flattens the hierarchial data structure
    // sort nodes to ensure that bigger nodes are drawn first
    // TBD collision detection and move nodes within the tree structure
    
    var nodes = _tree.nodes(treeData);
      ;//.filter(function(d) {return !d.values; });
    
    /*_tree.nodes(treeData)
      //.filter(function(d) {return !d.children; })
      .sort(function(a,b) {
        return d3.descending(_value(a), _value(b));
      });
    */
    console.log('treemap',raw,data,treeData,nodes.length,nodes);
    //d3.select('body').append('pre').text(JSON.stringify(treeData));
    
    
    var color = d3.scale.category20c();
    
    var cell = _treeG.selectAll("g.cell").data(nodes);
    console.log('cells',nodes,cell);
    
    cell.exit()
      .call(printSel,'cell exit')
      .remove();
    
    var cellEnt = cell.enter()
      .call(printSel,'cell enter')
      .append("svg:g").attr('class','cell');
    
    cellEnt.append("svg:rect");
    cellEnt.append("svg:text");
    cellEnt.append("title");
    
    
    /*
    cell
      .attr("class", "cell")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
      .on("click", function(d) { return zoom(node == d.parent ? root : d.parent); });

    cell.select("rect")
      .attr("width", function(d) { return d.dx - 1; })
      .attr("height", function(d) { return d.dy - 1; })
      .style("fill", function(d) { return color(d.key); });
    
    */
    
    
    cell
      .call(printSel,'cell update')
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    cell.select("rect")
        .call(printSel,'rect update')
        .attr("width", function(d) { return d.dx - 1; })
        .attr("height", function(d) { return d.dy - 1; })
        .style("fill", function(d) { return d3.rgb(color(d.parent ? (d.parent.key) : "")).brighter(); })
        .style("fill-opacity", function(d) { return d.progress / 100; })
        .style("stroke", function(d) {return color(d.parent ? (d.parent.key) : ""); });

    cell.select("text")
        .call(printSel,'text update')
        .attr("x", function(d) { return d.dx / 2; })
        .attr("y", function(d) { return d.dy / 2; })
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .text(function(d) { return d.key.split('SH2-')[1]; })
        .style("opacity", function(d) { d.w = this.getComputedTextLength(); return d.dx > d.w ? 1 : 0; });
    
    cell.select("title")
      .text(function(d) {
        return d.key +":" + d.value;
      });
    
    
    
    /*
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
    */
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
