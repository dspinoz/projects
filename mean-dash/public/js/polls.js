// Angular module, defining routes for the app

angular.module('polls', ['pollServices'])
  .config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/polls', { templateUrl: '/polls/list.html', controller: PollListCtrl }).
      when('/poll/:pollId', { templateUrl: '/polls/item.html', controller: PollItemCtrl }).
      when('/new', { templateUrl: '/polls/new.html', controller: PollNewCtrl }).
      otherwise({ redirectTo: '/polls' });
  }]);
