'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:CaseController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('CaseController', ['$scope', '$state', '$stateParams', 'TableFactory', function($scope, $state, $stateParams, TableFactory) {

        init();
        $scope.projectSelect = "";
        $scope.funcTestCase = ['test1func', 'test2func', 'test3func', 'test4func'];
        $scope.yardStickCase = ['test1yard', 'test2yard', 'test3yard', 'test4yard'];
        $scope.bottleNeckCase = ['test1bottle', 'test2bottle', 'test3bottle', 'test4bottle',
            'test5bottle', 'test6bottle', 'test7bottle', 'test8bottle',
            'test9bottle', 'test10bottle', 'test11bottle', 'test12bottle',
            'test13bottle', 'test14bottle', 'test15bottle', 'test16bottle',
            'test17bottle', 'test18bottle', 'test19bottle', 'test20bottle'
        ];
        $scope.selectedFunc = ["test1func"];
        $scope.selectBottle = ["test8bottle"];
        $scope.versionlist = ["Colorado", "Master"];
        $scope.VersionOption = [
            { title: 'Colorado' },
            { title: 'Master' }
        ];
        $scope.VersionConfig = {
            create: true,
            valueField: 'title',
            labelField: 'title',
            delimiter: '|',
            maxItems: 1,
            placeholder: 'Version',
            onChange: function(value) {
                checkElementArrayValue($scope.selection, $scope.VersionOption);
                $scope.selection.push(value);
                // console.log($scope.selection);

            }
        };


        function init() {
            $scope.toggleSelection = toggleSelection;
            $scope.toggleSelectionMulti = toggleSelectionMulti;

        }

        function toggleSelection(status) {
            // var idx = $scope.weekselection.indexOf(status);
            $scope.projectSelect = status;

        }

        function toggleSelectionMulti(status) {
            var idx = $scope.selection.indexOf(status);

            if (idx > -1) {
                $scope.selection.splice(idx, 1);
            } else {
                $scope.selection.push(status);
            }
            console.log($scope.selection);
        }


    }]);