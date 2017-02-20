'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:MainPageController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('MainController', ['$scope', '$state', '$stateParams', function($scope, $state, $stateParams) {

        init();

        function init() {
            $scope.goTest = goTest;
            $scope.goLogin = goLogin;

        }

        function goTest() {
            $state.go("select.selectTestCase");
        }

        function goLogin() {
            $state.go("login");
        }




    }]);