'use strict';

/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.controller:TableController
 * @description
 * # TableController
 * Controller of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .controller('TableController', ['$scope', '$state', '$stateParams', 'TableFactory', function ($scope, $state, $stateParams, TableFactory) {

        $scope.filterlist = [];
        $scope.selection = [];
        $scope.statusList = ["Success", "Warning", "Danger"];
        $scope.projectList = ["Deployment", "Functest", "Yardstick"];
        $scope.installerList = ["apex", "compass", "fuel", "joid"];
        $scope.versionlist = ["Colorado", "Master"];
        $scope.loopci = ["Daily", "Weekly", "Monthly"];
        $scope.time = ["10 days", "1 Month"];
        $scope.tableDataAll = {};
        $scope.tableInfoAll = {};



        $scope.scenario =
            {
                "scenarios": {
                    "os-nosdn-kvm-noha": {
                        "status": "Success",
                        "installers": {
                            "apex": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS",


                                },
                                {
                                    "project": "Functest",
                                    "score": "null",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "compass": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "fuel": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "joid": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ]
                        }
                    },
                    "os-nosdn-ovs-ha": {
                        "status": "Danger",
                        "installers": {
                            "apex": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS",


                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "compass": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "fuel": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "joid": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ]
                        }
                    },
                    "os-nosdn-ovs-noha": {
                        "status": "Warning",
                        "installers": {
                            "apex": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS",


                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "compass": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "fuel": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ],
                            "joid": [
                                {
                                    "project": "Deployment",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Functest",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                },
                                {
                                    "project": "Yardstick",
                                    "score": "13/14",
                                    "status": "SUCCESS"
                                }
                            ]
                        }
                    }
                }
            };

        // var headData = Object.keys($scope.scenario.scenarios.os_nosdn_kvm_noha.installers);
        // $scope.headData = headData;
        //construct json
        function constructJson() {

            var colspan;
            var InstallerData;
            var projectsInfo;
            $scope.tableDataAll["scenario"] = [];


            for (var item in $scope.scenario.scenarios) {




                var headData = Object.keys($scope.scenario.scenarios[item].installers);
                var scenarioStatus = $scope.scenario.scenarios[item].status;


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
                        temArray.push(projectData[j][k].score);
                        temArray.push(projectData[j][k].project);
                        temArray.push(headData[j]);
                        datadisplay.push(temArray);

                    }

                }

                colspan = projects.length / headData.length;

                var tabledata = {
                    scenarioName: item, Installer: InstallerData, projectData: projectData, projects: projects,
                    datadisplay: datadisplay, colspan: colspan, status: scenarioStatus
                };

                JSON.stringify(tabledata);
                $scope.tableDataAll.scenario.push(tabledata);

            }


            projectsInfo = $scope.tableDataAll.scenario[0].projects;

            var tempHeadData = [];



            for (var i = 0; i < InstallerData.length; i++) {
                for (var j = 0; j < colspan; j++) {
                    tempHeadData.push(InstallerData[i]);
                }
            }

            console.log(tempHeadData);

            var projectsInfoAll = [];

            for (var i = 0; i < projectsInfo.length; i++) {
                var tempA = [];
                tempA.push(projectsInfo[i]);
                tempA.push(tempHeadData[i]);
                projectsInfoAll.push(tempA);

            }
            console.log(projectsInfoAll);

            $scope.tableDataAll["colspan"] = colspan;
            $scope.tableDataAll["Installer"] = InstallerData;
            $scope.tableDataAll["Projects"] = projectsInfoAll;

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

        init();
        function init() {
            $scope.toggleSelection = toggleSelection;

            constructJson();

        }

        // $scope.test=false;

        var statusListString = $scope.statusList.toString();
        var projectListString = $scope.projectList.toString();
        var installerListString = $scope.installerList.toString();


        $scope.colspan=$scope.tableDataAll.colspan;
        //filter function
        function filterData() {


            $scope.selectInstallers = [];
            $scope.selectProjects = [];
            $scope.selectStatus = [];
            for (var i = 0; i < $scope.selection.length; i++) {
                if (statusListString.indexOf($scope.selection[i]) > -1) {
                    $scope.selectStatus.push($scope.selection[i]);
                }
                if (projectListString.indexOf($scope.selection[i]) > -1) {
                    $scope.selectProjects.push($scope.selection[i]);
                }
                if (installerListString.indexOf($scope.selection[i]) > -1) {
                    $scope.selectInstallers.push($scope.selection[i]);
                }
            }

            $scope.colspan=$scope.selectProjects.length;
            //when some selection is empty, we set it full
            if($scope.selectInstallers.length==0){
                $scope.selectInstallers=$scope.installerList;

            }
            if($scope.selectProjects.length==0){
                $scope.selectProjects=$scope.projectList;
                $scope.colspan=$scope.tableDataAll.colspan;
            }
            if($scope.selectStatus.length==0){
                $scope.selectStatus=$scope.statusList
            }
        }


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
            onChange: function (value) {
                checkElementArrayValue($scope.selection, $scope.VersionOption);
                $scope.selection.push(value);
                // console.log($scope.selection);

            }

        }

        $scope.LoopOption = [
            { title: 'Daily' },
            { title: 'Weekly' },
            { title: 'Monthly' }
        ];
        $scope.LoopConfig = {
            create: true,
            valueField: 'title',
            labelField: 'title',
            delimiter: '|',
            maxItems: 1,
            placeholder: 'Loop',
            onChange: function (value) {
                checkElementArrayValue($scope.selection, $scope.LoopOption);
                $scope.selection.push(value);
                // console.log($scope.selection);

            }
        }

        $scope.TimeOption = [
            { title: '10 days' },
            { title: '1 month' }
        ];
        $scope.TimeConfig = {
            create: true,
            valueField: 'title',
            labelField: 'title',
            delimiter: '|',
            maxItems: 1,
            placeholder: 'Time',
            onChange: function (value) {
                checkElementArrayValue($scope.selection, $scope.TimeOption);
                $scope.selection.push(value);
                // console.log($scope.selection)

            }
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
            }
            else {
                $scope.selection.push(status);
            }
            console.log($scope.selection);
            filterData();

        }

    }]);
