'use strict'
/**
 * @ngdoc function
 * @name opnfvdashBoardAngularApp.config:config.router.js
 * @description config of the ui router and lazy load setting
 * config of the opnfvdashBoardAngularApp
 */
angular.module('opnfvApp')
    .run([
        '$rootScope', '$state', '$stateParams',
        function($rootScope, $state, $stateParams) {

            $rootScope.$state = $state;
            $rootScope.$stateParams = $stateParams;

        }
    ]).config(['$stateProvider', '$urlRouterProvider',
        function($stateProvider, $urlRouterProvider) {

            $urlRouterProvider.otherwise('/landingpage/table');

            $stateProvider
                .state('landingpage', {
                    url: "/landingpage",
                    controller: 'MainController',
                    templateUrl: "views/main.html",
                    data: { pageTitle: '首页', specialClass: 'landing-page' },
                    resolve: {
                        controller: ['$ocLazyLoad', function($ocLazyLoad) {
                            return $ocLazyLoad.load([

                            ])
                        }]
                    }
                })
                .state('landingpage.table', {
                    url: "/table",
                    controller: 'TableController',
                    templateUrl: "views/commons/table.html",
                    resolve: {
                        controller: ['$ocLazyLoad', function($ocLazyLoad) {
                            return $ocLazyLoad.load([
                                // 'scripts/controllers/table.controller.js'


                            ])
                        }]
                    }
                })
                .state('select', {
                    url: '/select',
                    templateUrl: "views/testcase.html",
                    data: { specialClass: 'top-navigation' },

                })
                .state('select.selectTestCase', {
                    url: "/selectCase",
                    controller: 'CaseController',
                    templateUrl: "views/commons/selectTestcase.html",

                })
                .state('select.testlist', {
                    url: "/caselist",
                    templateUrl: "views/commons/testCaseList.html"
                })
                .state('select.admin', {
                    url: "/admin",
                    controller: 'AdminController',
                    templateUrl: "views/commons/admin.html"
                })
                .state('select.testVisual', {
                    url: "/visual",
                    controller: "testVisualController",
                    templateUrl: "views/commons/testCaseVisual.html"
                })
                // .state('admin', {
                //     url: '/admin',
                //     data: { specialClass: ' fixed-sidebar  pace-done' },
                //     templateUrl: "views/commons/admin.html"
                // })

        }
    ])
    .run();
