dc.mytreeChart = function (parent, chartGroup) {
    var _chart = dc.colorMixin(dc.marginMixin(dc.baseMixin({})));

    _chart._doRender = function () {
        _chart.resetSvg();
        return _chart;
    };

    _chart._doRedraw = function () {
        return _chart;
    };

    return _chart.anchor(parent, chartGroup);
};
