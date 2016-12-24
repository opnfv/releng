'use strict';

/**
 * @ngdoc directive
 * @name opnfvApp.directive:myDirective
 * @description
 * # myDirective
 */
angular.module('opnfvApp')
  .directive('myDirective', function () {
    return {
      template: '<div></div>',
      restrict: 'E',
      link: function postLink(scope, element, attrs) {
        element.text('this is the myDirective directive');
      }
    };
  });
