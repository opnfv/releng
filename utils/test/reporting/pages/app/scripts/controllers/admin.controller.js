'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:AdminController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('AdminController', ['$scope', '$state', '$stateParams', 'TableFactory', function($scope, $state, $stateParams, TableFactory) {

        init();
        $scope.showSelectValue = 0;
        $scope.scenarioList = ["os_nosdn_kvm_noha", "os_nosdn_kvm_no", "os_nosdn_kvm_"];

        function init() {}








    }]);