dc.mycalendarChart = function (parent, chartGroup) {
  var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));
  
  _chart._mandatoryAttributes(['dimension', 'group']);
  
  var _G;
  
  _chart._doRender = function () {
    _chart.resetSvg();
    
    var width = _chart.width() - _chart.margins().right - _chart.margins().left,
        height = _chart.height() - _chart.margins().top - _chart.margins().bottom;

    _G = _chart.svg()
        .attr("width", width + _chart.margins().right + _chart.margins().left)
        .attr("height", height + _chart.margins().top + _chart.margins().bottom)
      .append("g")
        .attr("transform", "translate(" + _chart.margins().left + "," + _chart.margins().top + ")");
    
    return _chart;
  };

  _chart._doRedraw = function () {
    return _chart;
  };

  return _chart.anchor(parent, chartGroup);
};
