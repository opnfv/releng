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

            $scope.filterlist = [];
            $scope.selection = [];
            $scope.statusList = [];
            $scope.projectList = [];
            $scope.installerList = [];
            $scope.versionlist = [];
            $scope.loopci = [];
            $scope.time = [];
            $scope.tableDataAll = {};
            $scope.tableInfoAll = {};
            $scope.scenario = {};
            // $scope.selectProjects = [];


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
                    checkElementArrayValue($scope.selection, $scope.LoopOption);
                    $scope.selection.push(value);
                    // console.log($scope.selection);
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
                    checkElementArrayValue($scope.selection, $scope.TimeOption);
                    $scope.selection.push(value);
                    // console.log($scope.selection)
                    getScenarioData();


                }
            }


            init();

            function init() {
                $scope.toggleSelection = toggleSelection;
                getScenarioData();
                getFilters();
            }

            function getFilters() {
                TableFactory.getFilter().get({

                }).$promise.then(function(response) {
                    if (response != null) {
                        $scope.statusList = response.filters.status;
                        $scope.projectList = response.filters.projects;
                        $scope.installerList = response.filters.installers;
                        $scope.versionlist = response.filters.version;
                        $scope.loopci = response.filters.loops;
                        $scope.time = response.filters.time;

                        $scope.statusListString = $scope.statusList.toString();
                        $scope.projectListString = $scope.projectList.toString();
                        $scope.installerListString = $scope.installerList.toString();
                        $scope.VersionSelected = $scope.versionlist[1];
                        $scope.LoopCiSelected = $scope.loopci[0];
                        $scope.TimeSelected = $scope.time[0];
                        radioSetting($scope.versionlist, $scope.loopci, $scope.time);

                    } else {
                        alert("网络错误");
                    }
                })
            }

            function getScenarioData() {

                // var utl = BASE_URL + '/scenarios';
                var data = {
                    'status': ['success', 'danger', 'warning'],
                    'projects': ['functest', 'yardstick'],
                    'installers': ['apex', 'compass', 'fuel', 'joid'],
                    'version': $scope.VersionSelected,
                    'loops': $scope.LoopCiSelected,
                    'time': $scope.TimeSelected
                };

                TableFactory.getScenario(data).then(function(response) {
                    if (response.status == 200) {
                        $scope.scenario = response.data;

                        reSettingcolspan();
                    }

                }, function(error) {

                })

            }

            function reSettingcolspan() {
                if ($scope.selectProjects == undefined || $scope.selectProjects == null) {
                    constructJson();
                    $scope.colspan = $scope.tableDataAll.colspan;

                } else {
                    constructJson();
                    $scope.colspan = $scope.tempColspan;
                }
                // console.log("test")
            }

            //construct json 
            function constructJson(selectProject) {

                var colspan;
                var InstallerData;
                var projectsInfo;
                $scope.tableDataAll["scenario"] = [];


                for (var item in $scope.scenario.scenarios) {

                    var headData = Object.keys($scope.scenario.scenarios[item].installers).sort();
                    var scenarioStatus = $scope.scenario.scenarios[item].status;
                    var scenarioStatusDisplay;
                    if (scenarioStatus == "success") {
                        scenarioStatusDisplay = "navy";
                    } else if (scenarioStatus == "danger") {
                        scenarioStatusDisplay = "danger";
                    } else if (scenarioStatus == "warning") {
                        scenarioStatusDisplay = "warning";
                    }

                    InstallerData = headData;
                    var projectData = [];
                    var datadisplay = [];
                    var projects = [];

                    for (var j = 0; j < headData.length; j++) {

                        projectData.push($scope.scenario.scenarios[item].installers[headData[j]]);
                    }
                    for (var j = 0; j < projectData.length; j++) {

                        for (var k = 0; k < projectData[j].length; k++) {
                            projects.push(projectData[j][k].project);
                            var temArray = [];
                            if (projectData[j][k].score == null) {
                                temArray.push("null");
                                temArray.push(projectData[j][k].project);
                                temArray.push(headData[j]);
                            } else {
                                temArray.push(projectData[j][k].score);
                                temArray.push(projectData[j][k].project);
                                temArray.push(headData[j]);
                            }


                            if (projectData[j][k].status == "platinium") {
                                temArray.push("primary");
                                temArray.push("P");
                            } else if (projectData[j][k].status == "gold") {
                                temArray.push("danger");
                                temArray.push("G");
                            } else if (projectData[j][k].status == "silver") {
                                temArray.push("warning");
                                temArray.push("S");
                            } else if (projectData[j][k].status == null) {
                                temArray.push("null");
                            }

                            datadisplay.push(temArray);

                        }

                    }

                    colspan = projects.length / headData.length;

                    var tabledata = {
                        scenarioName: item,
                        Installer: InstallerData,
                        projectData: projectData,
                        projects: projects,
                        datadisplay: datadisplay,
                        colspan: colspan,
                        status: scenarioStatus,
                        statusDisplay: scenarioStatusDisplay
                    };

                    JSON.stringify(tabledata);
                    $scope.tableDataAll.scenario.push(tabledata);


                    // console.log(tabledata);

                }


                projectsInfo = $scope.tableDataAll.scenario[0].projects;

                var tempHeadData = [];

                for (var i = 0; i < InstallerData.length; i++) {
                    for (var j = 0; j < colspan; j++) {
                        tempHeadData.push(InstallerData[i]);
                    }
                }

                //console.log(tempHeadData);

                var projectsInfoAll = [];

                for (var i = 0; i < projectsInfo.length; i++) {
                    var tempA = [];
                    tempA.push(projectsInfo[i]);
                    tempA.push(tempHeadData[i]);
                    projectsInfoAll.push(tempA);

                }
                //console.log(projectsInfoAll);

                $scope.tableDataAll["colspan"] = colspan;
                $scope.tableDataAll["Installer"] = InstallerData;
                $scope.tableDataAll["Projects"] = projectsInfoAll;

                // console.log($scope.tableDataAll);
                $scope.colspan = $scope.tableDataAll.colspan;
                console.log($scope.tableDataAll);

            }

            //get json element size
            function getSize(jsondata) {
                var size = 0;
                for (var item in jsondata) {
                    size++;
                }
                return size;
            }


            // console.log($scope.colspan);


            //find all same element index 
            function getSameElementIndex(array, element) {
                var indices = [];
                var idx = array.indexOf(element);
                while (idx != -1) {
                    indices.push(idx);
                    idx = array.indexOf(element, idx + 1);
                }
                //return indices;
                var result = { element: element, index: indices };
                JSON.stringify(result);
                return result;
            }

            //delete element in array
            function deletElement(array, index) {
                array.splice(index, 1);

            }

            function radioSetting(array1, array2, array3) {
                var tempVersion = [];
                var tempLoop = [];
                var tempTime = [];
                for (var i = 0; i < array1.length; i++) {
                    var temp = {
                        title: array1[i]
                    };
                    tempVersion.push(temp);
                }
                for (var i = 0; i < array2.length; i++) {
                    var temp = {
                        title: array2[i]
                    };
                    tempLoop.push(temp);
                }
                for (var i = 0; i < array3.length; i++) {
                    var temp = {
                        title: array3[i]
                    };
                    tempTime.push(temp);
                }
                $scope.VersionOption = tempVersion;
                $scope.LoopOption = tempLoop;
                $scope.TimeOption = tempTime;
            }

            //remove element in the array
            function removeArrayValue(arr, value) {
                for (var i = 0; i < arr.length; i++) {
                    if (arr[i] == value) {
                        arr.splice(i, 1);
                        break;
                    }
                }
            }

            //check if exist element
            function checkElementArrayValue(arrayA, arrayB) {
                for (var i = 0; i < arrayB.length; i++) {
                    if (arrayA.indexOf(arrayB[i].title) > -1) {
                        removeArrayValue(arrayA, arrayB[i].title);
                    }
                }
            }

            function toggleSelection(status) {
                var idx = $scope.selection.indexOf(status);

                if (idx > -1) {
                    $scope.selection.splice(idx, 1);
                    filterData($scope.selection)
                } else {
                    $scope.selection.push(status);
                    filterData($scope.selection)
                }
                // console.log($scope.selection);

            }

            //filter function
            function filterData(selection) {

                $scope.selectInstallers = [];
                $scope.selectProjects = [];
                $scope.selectStatus = [];
                for (var i = 0; i < selection.length; i++) {
                    if ($scope.statusListString.indexOf(selection[i]) > -1) {
                        $scope.selectStatus.push(selection[i]);
                    }
                    if ($scope.projectListString.indexOf(selection[i]) > -1) {
                        $scope.selectProjects.push(selection[i]);
                    }
                    if ($scope.installerListString.indexOf(selection[i]) > -1) {
                        $scope.selectInstallers.push(selection[i]);
                    }
                }


                // $scope.colspan = $scope.selectProjects.length;
                //when some selection is empty, we set it full
                if ($scope.selectInstallers.length == 0) {
                    $scope.selectInstallers = $scope.installerList;

                }
                if ($scope.selectProjects.length == 0) {
                    $scope.selectProjects = $scope.projectList;
                    $scope.colspan = $scope.tableDataAll.colspan;
                } else {
                    $scope.colspan = $scope.selectProjects.length;
                    $scope.tempColspan = $scope.colspan;
                }
                if ($scope.selectStatus.length == 0) {
                    $scope.selectStatus = $scope.statusList
                }

                // console.log($scope.selectStatus);
                // console.log($scope.selectProjects);

            }


        }
    ]);