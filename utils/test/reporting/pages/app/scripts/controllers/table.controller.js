'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:TableController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('TableController', ['$scope', '$state', '$stateParams', '$http', 'TableFactory', '$timeout',
        function($scope, $state, $stateParams, $http, TableFactory, $timeout) {

            init();

            function init() {
                $scope.filterlist = [];
                $scope.selection = [];

                $scope.statusList = [];
                $scope.projectList = [];
                $scope.installerList = [];
                $scope.versionlist = [];
                $scope.loopList = [];
                $scope.timeList = [];

                $scope.selectStatus = [];
                $scope.selectProjects = [];
                $scope.selectInstallers = [];
                $scope.selectVersion = null;
                $scope.selectLoop = null;
                $scope.selectTime = null;

                $scope.statusClicked = false;
                $scope.installerClicked = false;
                $scope.projectClicked = false;

                $scope.scenarios = {};

                $scope.VersionConfig = {
                    create: true,
                    valueField: 'title',
                    labelField: 'title',
                    delimiter: '|',
                    maxItems: 1,
                    placeholder: 'Version',
                    onChange: function(value) {
                        $scope.selectVersion = value;

                        getScenarioData();

                    }
                }

                $scope.LoopConfig = {
                    create: true,
                    valueField: 'title',
                    labelField: 'title',
                    delimiter: '|',
                    maxItems: 1,
                    placeholder: 'Loop',
                    onChange: function(value) {
                        $scope.selectLoop = value;

                        getScenarioData();

                    }
                }

                $scope.TimeConfig = {
                    create: true,
                    valueField: 'title',
                    labelField: 'title',
                    delimiter: '|',
                    maxItems: 1,
                    placeholder: 'Time',
                    onChange: function(value) {
                        $scope.selectTime = value;

                        getScenarioData();
                    }
                }

                getFilters();
            }

            function getFilters() {
                TableFactory.getFilter().get({
                }).$promise.then(function(response) {
                    if (response != null) {
                        $scope.statusList = response.filters.status;
                        $scope.projectList = response.filters.projects;
                        $scope.installerList = response.filters.installers;
                        $scope.versionList = toSelectList(response.filters.version);
                        $scope.loopList = toSelectList(response.filters.loops);
                        $scope.timeList = toSelectList(response.filters.time);

                        $scope.selectStatus = copy($scope.statusList);
                        $scope.selectInstallers = copy($scope.installerList);
                        $scope.selectProjects = copy($scope.projectList);
                        $scope.selectVersion = response.filters.version[0];
                        $scope.selectLoop = response.filters.loops[0];
                        $scope.selectTime = response.filters.time[0];

                        getScenarioData();

                    } else {
                    }
                });
            }

            function toSelectList(arr){
                var tempList = [];
                angular.forEach(arr, function(ele){
                    tempList.push({'title': ele});
                });
                return tempList;
            }

            function copy(arr){
                var tempList = [];
                angular.forEach(arr, function(ele){
                    tempList.push(ele);
                });
                return tempList;
            }

            function getScenarioData() {

                var data = {
                    'status': $scope.selectStatus,
                    'projects': $scope.selectProjects,
                    'installers': $scope.selectInstallers,
                    'version': $scope.selectVersion,
                    'loops': $scope.selectLoop,
                    'time': $scope.selectTime
                };

                TableFactory.getScenario(data).then(function(response) {
                    if (response.status == 200) {
                        $scope.scenarios = response.data.scenarios;
                        getScenario();
                    }

                }, function(error) {
                });

            }

            function getScenario(){

                $scope.project_row = [];
                angular.forEach($scope.selectInstallers, function(installer){
                    angular.forEach($scope.selectProjects, function(project){
                        var temp = {
                            'installer': installer,
                            'project': project
                        }
                        $scope.project_row.push(temp);

                    });
                });


                $scope.scenario_rows = [];
                angular.forEach($scope.scenarios, function(scenario, name){
                    var scenario_row = {
                        'name': null,
                        'status': null,
                        'statusDisplay': null,
                        'datadisplay': [],
                    };
                    scenario_row.name = name;
                    scenario_row.status = scenario.status;

                    var scenarioStatusDisplay;
                    if (scenario.status == "success") {
                        scenarioStatusDisplay = "navy";
                    } else if (scenario.status == "danger") {
                        scenarioStatusDisplay = "danger";
                    } else if (scenario.status == "warning") {
                        scenarioStatusDisplay = "warning";
                    }
                    scenario_row.statusDisplay = scenarioStatusDisplay;

                    angular.forEach($scope.selectInstallers, function(installer){
                        angular.forEach($scope.selectProjects, function(project){
                            var datadisplay = {
                                'installer': null,
                                'project': null,
                                'value': null,
                                'label': null,
                                'label_value': null
                            };
                            datadisplay.installer = installer;
                            datadisplay.project = project;
                            datadisplay.value = scenario.installers[installer][project].score;

                            var single_status = scenario.installers[installer][project].status;
                            if (single_status == "platinium") {
                                datadisplay.label = 'primary';
                                datadisplay.label_value = 'P';
                            } else if (single_status == "gold") {
                                datadisplay.label = 'danger';
                                datadisplay.label_value = 'G';
                            } else if (single_status == "silver") {
                                datadisplay.label = 'warning';
                                datadisplay.label_value = 'S';
                            } else if (single_status == null) {
                            }
                            scenario_row.datadisplay.push(datadisplay);

                        });
                    });
                    $scope.scenario_rows.push(scenario_row);
                });
            }


            function clickBase(eleList, ele){
                var idx = eleList.indexOf(ele);
                if(idx > -1){
                    eleList.splice(idx, 1);
                }else{
                    eleList.push(ele);
                }
            }

            $scope.clickStatus = function(status){
                if($scope.selectStatus.length == $scope.statusList.length && $scope.statusClicked == false){
                    $scope.selectStatus = [];
                    $scope.statusClicked = true;
                }

                clickBase($scope.selectStatus, status);

                if($scope.selectStatus.length == 0 && $scope.statusClicked == true){
                    $scope.selectStatus = copy($scope.statusList);
                    $scope.statusClicked = false;
                }

                getScenarioData();
            }

            $scope.clickInstaller = function(installer){
                if($scope.selectInstallers.length == $scope.installerList.length && $scope.installerClicked == false){
                    $scope.selectInstallers = [];
                    $scope.installerClicked = true;
                }

                clickBase($scope.selectInstallers, installer);

                if($scope.selectInstallers.length == 0 && $scope.installerClicked == true){
                    $scope.selectInstallers = copy($scope.installerList);
                    $scope.installerClicked = false;
                }

                getScenarioData();
            }

            $scope.clickProject = function(project){
                if($scope.selectProjects.length == $scope.projectList.length && $scope.projectClicked == false){
                    $scope.selectProjects = [];
                    $scope.projectClicked = true;
                }

                clickBase($scope.selectProjects, project);

                if($scope.selectProjects.length == 0 && $scope.projectClicked == true){
                    $scope.selectProjects = copy($scope.projectList);
                    $scope.projectClicked = false;
                }

                getScenarioData();
            }

        }
    ]);
