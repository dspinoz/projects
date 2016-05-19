dc.mycalendarChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension', 'group']);
  
  // TBD move color styles to here
  // based on "d3 Calendar View" by mbostock
  _chart.colors(d3.scale.quantize()
    .domain([-.05, .05])
    .range(d3.range(11).map(function(d) { return "q" + d + "-11"; })));
    
  _chart.colorAccessor(function(d) { return d.value; });
  
  var _G;
  var _width, _height;
  
  var _yearFormat = d3.time.format('%Y'),
      _monthFormat = d3.time.format('%m'),
      _cellSize = 5, // TBD dynamically calculate rect.day size based on width/height
      _textHeight = 12; //TBD dynamically calculate year.text size
      
      
  var _title = function(d) { return d.key + ": " + d.value; };
      
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
  
    /*
    var p = _chart.selectAll('p').data(['a']);
    p.exit().remove();
    p.enter().append('p');
    p.text(function(d) { return JSON.stringify(d); });
    */
    
    var keyExtent = d3.extent(data, function(d) { return d.key; });
    _chart.colors().domain(d3.extent(data, function(d) { return d.value; }));
    
    var begin = d3.time.year(keyExtent[0]), 
        end = d3.time.year(keyExtent[1]);
    
    // TBD is this correct for all data?
    // modify extent so that time range shows all data
    var ybegin = new Date(begin), yend = new Date(end);
    yend.setFullYear(yend.getFullYear()+1);
    var dbegin = new Date(begin), dend = new Date(end);
    dbegin.setDate(dbegin.getDate()+1);
    dend.setDate(dend.getDate()+1);
    
    //p.append('p').text(JSON.stringify(d3.time.days(dbegin,dend)));
    
    var years = d3.time.years(ybegin,yend);
    
    var year = _G.selectAll("g.year").data(years);
    
    year.exit().remove();
    
	 // group svg element types and keep months on top 
    var yEnter = year.enter().append("g")
		.attr('class', 'year');
    yEnter.append('g').attr('class', 'days RdYlGn '); //TBD move style to here
    yEnter.append('g').attr('class', 'months');
				
    year
      .attr("transform", function(d,i) { 
        return "translate(0," + (((_cellSize*7)+_textHeight)*i) + ")";
      });
    
    var yearText = year.selectAll('text').data(function(d) { return [d]; });
    
    yearText.exit().remove();
    
    yearText.enter().append('text')
        .attr("transform", "translate(-6," + _cellSize * 3.5 + ")rotate(-90)")
        .style("text-anchor", "middle");
        
    yearText.text(function(d) { return _yearFormat(d); });
    
    
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
      
    month.attr("d", monthPath);
    
    
    var day = year.select('g.days').selectAll(".day")
      .data(function(d) { 
        var days = d3.time.days(new Date(+_yearFormat(d), 0, 1), new Date(+_yearFormat(d) + 1, 0, 1)); 
        
        var data = [];
        
        days.forEach(function(d) {
          data.push({_date: d, width: _cellSize});
        });
        
        return data;
      });
      
    day.exit().remove();
      
    day.enter().append("rect")
      .attr("class", "day")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.width; })
      .on('click', function() {
        var d = d3.select(this).datum();
        _chart.onClick(d);
      })
      /*
      .on('mouseover',function(d) {
        // TBD darker color
        d3.select(this).classed('selected', d._selected = !d._selected);
        console.log('day', d);
      })
      .on('mouseout',function (d) {
        d._selected = !d._selected;
        
        d3.select(this)
          .attr("class", function(d,i) {
            return 'day ' + _chart.getColor(d,i); 
          });
      })
      */
      .append('title');
    
    day.attr("x", function(d) { return d3.time.weekOfYear(d._date) * d.width; })
      .attr("y", function(d) { return d._date.getDay() * d.width; });
    

    
    var map = d3.map(data, function(d) { return d.key; });
    
    var dataDays = day
      .filter(function(d) { 
        if (map.has(d._date)) {
          d.key = d._date;
          d.value = map.get(d._date).value;
          return true;
        }
        
        return false;
      });
      
    dataDays.attr("class", function(d,i) {
      return 'day ' + _chart.getColor(d,i);
    });
    
    dataDays.select('title').text(_chart.title());
    
    
    /*
    _day.append("title")
        .text(function(d) { return _titleFormat(_format.parse(d)); });
    */
    
  
    return _chart;
  };
  
  function monthPath(t0) {
    var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
        d0 = t0.getDay(), w0 = d3.time.weekOfYear(t0),
        d1 = t1.getDay(), w1 = d3.time.weekOfYear(t1);
    return "M" + (w0 + 1) * _cellSize + "," + d0 * _cellSize 
        + "H" + w0 * _cellSize + "V" + 7 * _cellSize
        + "H" + w1 * _cellSize + "V" + (d1 + 1) * _cellSize
        + "H" + (w1 + 1) * _cellSize + "V" + 0
        + "H" + (w0 + 1) * _cellSize + "Z";
  }

  
  _chart.title = function (f) {
    if (!arguments.length) {
      return _title;
    }
    _title = f;
    return _chart;
  };
  
  return _chart.anchor(parent, chartGroup);
};
