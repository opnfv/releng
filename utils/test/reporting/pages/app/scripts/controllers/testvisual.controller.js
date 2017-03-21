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
            $scope.dovet = "59,222,156,317";
            $scope.functest = "203,163,334,365";
            $scope.yardstick = "398,161,513,384";
            $scope.vsperf = "567,163,673,350";
            $scope.stor = "686,165,789,341";
            $scope.qtip = "802,164,905,341";
            $scope.bootleneck = "917,161,1022,338";
            $scope.noPopArea1 = "30,11,1243,146";
            $scope.noPopArea2 = "1041,157,1250,561";
            $scope.noPopArea3 = "15,392,1027,561";

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
                        $loading.finish('Key');


                    }
                })
            }

            function getDetail(casename) {
                TableFactory.getProjectTestCaseDetail().get({
                    'project': $scope.modalName,
                    'testcase': casename
                }).$promise.then(function(response) {
                    if (response != null) {
                        $scope.project_name_modal = response.project_name;
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