'use strict';

angular.module('mean').controller('PollsController', ['$scope', 'Global',
    function($scope, Global, Polls) {
        $scope.global = Global;
        $scope.polls = {
            name: 'polls'
        };
    }
]);
