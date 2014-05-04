'use strict';

angular.module('mean').config(['$stateProvider',
    function($stateProvider) {
        $stateProvider.state('polls example page', {
            url: '/polls/example',
            templateUrl: 'polls/views/index.html'
        });
    }
]);
