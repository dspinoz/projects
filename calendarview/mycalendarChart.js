dc.mycalendarChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension', 'group']);
  
  // TBD move color styles to here
  // based on "d3 Calendar View" by mbostock
  _chart.linearColors(["#FFEAEA", "#FF0000"]);
    
  _chart.colorAccessor(function(d) { return d.value; });
  
  var _G;
  var _width, _height;
  
  var _yearFormat = d3.time.format('%Y'),
      _monthFormat = d3.time.format('%m'),
      _cellWidth = 0, 
      _cellHeight = 0, 
      _textHeight = 12; //TBD dynamically calculate year.text size
      
  var _title = function(d) { return d.key + ": " + d.value; };
  var _key = function(d) { return d.key; };
  var _value = function(d) { return d.value; };
  var _valueFilter = function(d) { return d.value.toFixed(1) > 0; };
  
  _chart._doRender = function () {
    _chart.resetSvg();
    
    _width = _chart.width() - _chart.margins().right - _chart.margins().left;
    _height = _chart.height() - _chart.margins().top - _chart.margins().bottom;

    _G = _chart.svg()
        .attr("width", _width + _chart.margins().right + _chart.margins().left)
        .attr("height", _height + _chart.margins().top + _chart.margins().bottom)
      .append("g")
        .attr("transform", "translate(" + _chart.margins().left + "," + _chart.margins().top + ")");
    
    _chart.redraw();
    
    return _chart;
  };

  _chart._doRedraw = function () {
  
    var data = _chart.group().all();
  
    var keyExtent = d3.extent(data, _chart.key());
    _chart.colors().domain(d3.extent(data, _chart.value()));
    
    var begin = d3.time.year(keyExtent[0]), 
        end = d3.time.year(keyExtent[1]);
    
    // TBD is this correct for all data?
    // modify extent so that time range shows all data
    var ybegin = new Date(begin), yend = new Date(end);
    yend.setFullYear(yend.getFullYear()+1);
    
    
    var years = d3.time.years(ybegin,yend);
    
    if (!_cellWidth) {
      _cellWidth = _width / 53; //53 is max weeks in year
    }
    
    if (!_cellHeight) {
      _cellHeight = _height / 7 / years.length; // 7 is max days in week
    }
    
    
    var year = _G.selectAll("g.year").data(years);
    
    year.exit().remove();
    
	 // group svg element types and keep months on top 
    var yEnter = year.enter().append("g")
		.attr('class', 'year');
    yEnter.append('g').attr('class', 'days');
    yEnter.append('g').attr('class', 'months');
				
    year.transition()
      .attr("transform", function(d,i) { 
        return "translate(0," + (((_cellHeight*7)+_textHeight)*i) + ")";
      });
    
    var yearText = year.selectAll('text').data(function(d) { return [d]; });
    
    yearText.exit().remove();
    
    yearText.enter().append('text')
        .attr("transform", "translate(-6," + _cellHeight * 3.5 + ")rotate(-90)")
        .style("text-anchor", "middle");
        
    yearText.transition()
      .text(function(d) { return _yearFormat(d); });
    
    
    var month = year.select('g.months').selectAll(".month")
      .data(function(d) {
        var months = d3.time.months(new Date(+_yearFormat(d), +_monthFormat(d) -1, 1), 
                                    new Date(+_yearFormat(d)+1, +_monthFormat(d)-1, 1));
        
        var data = [];
        
        months.forEach(function(d) {
          data.push(d);
        });
        
        return data;
      });
      
    month.exit().remove();
    
    month.enter().append("path")
      .attr("class", "month")
      .style("fill", "none")
      .style("stroke", "#555")
      .style("stroke-width", "1px");
      
    month.transition()
      .attr("d", monthPath);
    
    
    var day = year.select('g.days').selectAll(".day")
      .data(function(d) { 
        var days = d3.time.days(new Date(+_yearFormat(d), 0, 1), new Date(+_yearFormat(d) + 1, 0, 1)); 
        
        var data = [];
        
        days.forEach(function(d) {
          data.push({_date: d, height: _cellHeight, width: _cellWidth});
        });
        
        return data;
      });
      
    day.exit().remove();
      
    day.enter().append("rect")
      .attr("class", "day")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.height; })
      .on('click', function() {
        var d = d3.select(this).datum();
        
        if (_chart.value()(d) != undefined) {        
          _chart.onClick(d);
          _chart.redraw();
        }
      })
      .on('mouseover', function() {
        var d = d3.select(this).datum();
        
        d3.select(this).call(dayStyle, 
          // check for bound data, and verify value filter as other chart filters can affect the value
          (_chart.value()(d) != undefined &&  _chart.valueFilter()(d)), 
          // always highlight the current day
          true);
      })
      .on('mouseout', function() {
        var d = d3.select(this).datum();
        
        d3.select(this).call(dayStyle, 
          // check for bound data, and verify value filter as other chart filters can affect the value
          (_chart.value()(d) != undefined &&  _chart.valueFilter()(d)), 
          // see if the day is filtered to retain style
          _chart.filters().filter(function(f) {
            if (_chart.value()(d) == undefined) return false;
            return f.getTime() == _chart.key()(d).getTime();
          }).length != 0);
      })
      .append('title');
    
    day.transition()
      .attr("x", function(d) { return d3.time.weekOfYear(d._date) * d.width; })
      .attr("y", function(d) { return d._date.getDay() * d.height; });
      
    // no data attached and not filtered
    day.call(dayStyle, false, false);
    
    day.select('title')
      .text(function(d,i) {
        var tmp = {key: d._date, value: undefined};
        return _chart.title()(tmp);
      });
    
    
    var map = d3.map(data, _chart.key());
    
    var dataDays = day
      .filter(function(d) { 
        if (map.has(d._date)) {
          
          d.key = d._date;
          d.value = map.get(d._date).value;
          
          if (_chart.valueFilter()(d))
            return true;
        }
        
        return false;
      });
      
    // data attached, not filtered
    dataDays.call(dayStyle, true, false);
    
    dataDays.select('title').text(_chart.title());
    
    
    var set = d3.set(_chart.filters());
    
    var filteredDays = day
      .filter(function(d) { 
        if (set.has(d._date)) {
          
          d.key = d._date;
          d.value = map.get(d._date).value;
          
          if (_chart.valueFilter()(d))
            return true;
        }
        
        return false;
      });
    
    // data attached, filtered
    filteredDays.call(dayStyle, true, true);
    
    return _chart;
  };
  
  function dayStyle(selection, hasData, isFiltered) {
    
    if (!hasData) {
      //reset style as no data is attached
      selection
        .style('stroke-width', 1)
        .style('stroke', '#ccc')
        .style('fill', '#fff')
        .classed('highlight', false);
      return;
    }
    
    if (hasData && isFiltered) {
      selection
        .style('fill', _chart.getColor)
        .style("stroke-width", 3)
        .style("stroke", function(d,i) {
          var color = d3.rgb(_chart.getColor(d,i));
          return color.darker();
        })
        .classed('deselected', false);
      return;
    }
    
    if (_chart.filters().length == 0) {
      selection
        .style('fill', _chart.getColor)
        .style('stroke-width', 1)
        .style('stroke', '#ccc');
    }
    else {
      selection
        .style('fill', null)
        .style('stroke-width', null)
        .style('stroke', null)
        .classed('deselected', true);
    }
  }
  
  function monthPath(t0) {
    var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
        d0 = t0.getDay(), w0 = d3.time.weekOfYear(t0),
        d1 = t1.getDay(), w1 = d3.time.weekOfYear(t1);
    return "M" + (w0 + 1) * _cellWidth + "," + d0 * _cellHeight 
        + "H" + w0 * _cellWidth + "V" + 7 * _cellHeight
        + "H" + w1 * _cellWidth + "V" + (d1 + 1) * _cellHeight
        + "H" + (w1 + 1) * _cellWidth + "V" + 0
        + "H" + (w0 + 1) * _cellWidth + "Z";
  }

  
  _chart.cellSize = function (f) {
    if (!arguments.length) {
      return _cellSize;
    }
    _cellWidth = f;
    _cellHeight = f;
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
  
  _chart.valueFilter = function (f) {
    if (!arguments.length) {
      return _valueFilter;
    }
    _valueFilter = f;
    return _chart;
  };
  
  _chart.title = function (f) {
    if (!arguments.length) {
      return _title;
    }
    _title = f;
    return _chart;
  };
  
  return _chart.anchor(parent, chartGroup);
};
