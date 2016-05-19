dc.mycalendarChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension', 'group']);
  
  var _G, _years, _months, _days;
  var _width, _height;
  
  var _yearFormat = d3.time.format('%Y'),
      _monthFormat = d3.time.format('%m'),
      _cellSize = 5, // TBD dynamically calculate rect.day size based on width/height
      _textHeight = 12; //TBD dynamically calculate year.text size
      
  _chart._doRender = function () {
    _chart.resetSvg();
    
    _width = _chart.width() - _chart.margins().right - _chart.margins().left;
    _height = _chart.height() - _chart.margins().top - _chart.margins().bottom;

    _G = _chart.svg()
        .attr("width", _width + _chart.margins().right + _chart.margins().left)
        .attr("height", _height + _chart.margins().top + _chart.margins().bottom)
      .append("g")
        .attr("transform", "translate(" + _chart.margins().left + "," + _chart.margins().top + ")");
    
    // ensure that items are painted in the correct order
    // months is last to give correct outline
    _years = _G.append('g').attr('class', 'years');
    _days = _G.append('g').attr('class', 'days');
    _months = _G.append('g').attr('class', 'months');
    
    _chart.redraw();
    
    return _chart;
  };

  _chart._doRedraw = function () {
  
    var data = _chart.dimension().top(Infinity);
  
  /*
    var p = _chart.selectAll('p').data(['a']);
    p.exit().remove();
    p.enter().append('p');
    p.text(function(d) { return JSON.stringify(d); });
    */
    
    var extent = d3.extent(data, function(d) { return d._date; });
    
    var begin = d3.time.year(extent[0]), 
        end = d3.time.year(extent[1]);
    
    // TBD is this correct for all data?
    // modify extent so that time range shows all data
    var ybegin = new Date(begin), yend = new Date(end);
    yend.setFullYear(yend.getFullYear()+1);
    var dbegin = new Date(begin), dend = new Date(end);
    dbegin.setDate(dbegin.getDate()+1);
    dend.setDate(dend.getDate()+1);
    
    //p.append('p').text(JSON.stringify(d3.time.days(dbegin,dend)));
    
    var years = d3.time.years(ybegin,yend),
        days = d3.time.days(dbegin,dend);
    
    var year = _G.selectAll("g.year").data(years);
    
    year.exit().remove();
    
    year.enter().append("g").attr('class', 'year');
    
    year
      .attr("transform", function(d,i) { 
        return "translate(0," + (((_cellSize*7)+_textHeight)*i) + ")";
      });
    
    var yearText = year.selectAll('text').data(function(d) { console.log('year', d); return [d]; });
    
    yearText.exit().remove();
    
    yearText.enter().append('text')
        .attr("transform", "translate(-6," + _cellSize * 3.5 + ")rotate(-90)")
        .style("text-anchor", "middle");
        
    yearText.text(function(d) { return _yearFormat(d); });
    
    var day = year.selectAll(".day")
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
      //.style("stroke", "#fff")
      //.style("stroke-width", "1px")
      .attr("width", function(d) { return d.width; })
      .attr("height", function(d) { return d.width; })
      /*
      .style("fill", "#fff")
      .on('click', function(d) {
        console.log('heatmap click', d, _map[d], d._clicked);
      
        if (d in _selected) {
          d3.select(this)
            .style("stroke", "#ccc")
            .style("stroke-width", "1px")
            .style("fill", "#fff");
          delete _selected[d];
        } 
        else {
          d3.select(this)
            .style("stroke", "#000")
            .style("stroke-width", "3px")
            .style("fill", "blue");
          _selected[d] = true;
        }
        
        _chart.onClick({key: d, value: _map[d]});
        
      })
      */
      .on('mouseover',function(d) {
        d._selected = !d._selected;
        d3.select(this).style('fill', 'red');
        console.log('day', d);
      })
      .on('mouseout',function (d) {
        d._selected = !d._selected;
        d3.select(this).style('fill', null);
      });
    
    day.attr("x", function(d) { return d3.time.weekOfYear(d._date) * d.width; })
      .attr("y", function(d) { return d._date.getDay() * d.width; });
    
    var month = year.selectAll(".month")
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

  return _chart.anchor(parent, chartGroup);
};
