'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:testVisualController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('testVisualController', ['$scope', '$state', '$stateParams', 'TableFactory', 'ngDialog', '$http', '$loading',
        function($scope, $state, $stateParams, TableFactory, ngDialog, $http, $loading) {
            $scope.dovet = "50,168,177,443";
            $scope.functest = "194,173,356,442";
            $scope.yardstick = "377,183,521,412";
            $scope.vsperf = "542,185,640,414";
            $scope.stor = "658,187,750,410";
            $scope.qtip = "769,190,852,416";
            $scope.bottlenecks = "870,192,983,419";
            $scope.noPopArea1 = "26,8,1190,180";
            $scope.noPopArea2 = "1018,193,1190,590";
            $scope.noPopArea3 = "37,455,1003,584";

            init();
            $scope.showSelectValue = 0;
            $scope.scenarioList = ["os_nosdn_kvm_noha", "os_nosdn_kvm_no", "os_nosdn_kvm_"];

            function init() {
                $scope.myTrigger = myTrigger;
                $scope.openTestDetail = openTestDetail;
                $scope.pop = pop;
                $scope.getDetail = getDetail;
                getUrl();



            }

            function myTrigger(name) {
                $loading.start('Key');
                $scope.tableData = null;
                $scope.modalName = name;

                var url = PROJECT_URL + '/projects/' + name + '/cases';

                var config = {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                    }
                }
                $http.get(url, config).then(function(response) {
                    if (response.status == 200) {
                        $scope.tableData = response.data;

                        $scope.tableData = constructObjectArray($scope.tableData);
                        console.log($scope.tableData);
                        $loading.finish('Key');



                    }
                })
            }

            //construct key value for tableData
            function constructObjectArray(array) {
                var templateArray = [];
                for (var i = 0; i < array.length; i++) {
                    var key = Object.keys(array[i])[0];
                    var value = array[i][key];
                    var temp = {
                        'key': key,
                        'value': value
                    };
                    templateArray.push(temp);

                }

                return templateArray;
            }

            function getDetail(casename) {
                TableFactory.getProjectTestCaseDetail().get({
                    'project': $scope.modalName,
                    'testcase': casename
                }).$promise.then(function(response) {
                    if (response != null) {
                        $scope.name_modal = response.name;
                        $scope.description_modal = response.description;
                        openTestDetail();
                    }
                })

            }


            function openTestDetail() {
                ngDialog.open({
                    template: 'views/modal/testcasedetail.html',
                    className: 'ngdialog-theme-default',
                    scope: $scope,
                    showClose: false
                })
            }

            function getUrl() {
                TableFactory.getProjectUrl().get({

                }).$promise.then(function(response) {
                    if (response != null) {
                        $scope.functesturl = response.functest;
                        $scope.yardstickurl = response.yardstick;
                        $scope.vsperfurl = response.vsperf;
                        $scope.storperfurl = response.storperf;
                        $scope.qtipurl = response.qtip;
                        $scope.bottlenecksurl = response.bottlenecks;
                        $scope.doveturl = null;
                    }
                })
            }










        }
    ]);
