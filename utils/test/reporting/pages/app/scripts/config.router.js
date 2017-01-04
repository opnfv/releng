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
        function ($rootScope, $state, $stateParams) {

            $rootScope.$state = $state;
            $rootScope.$stateParams = $stateParams;

        }
    ]
    ).config(['$stateProvider', '$urlRouterProvider',
        function ($stateProvider, $urlRouterProvider) {

            $urlRouterProvider.otherwise('/landingpage/table');

            $stateProvider
                .state('landingpage', {
                    url: "/landingpage",
                    //controller: 'MainCtrl',
                    templateUrl: "views/main.html",
                    data: { pageTitle: '首页', specialClass: 'landing-page' },
                    resolve: {
                        controller: ['$ocLazyLoad', function ($ocLazyLoad) {
                            return $ocLazyLoad.load([

                            ])
                        }]
                    }
                })
                .state('landingpage.table', {
                    url: "/table",
                    controller:'TableController',
                    templateUrl: "views/commons/table.html",
                    resolve: {
                        controller: ['$ocLazyLoad', function ($ocLazyLoad) {
                            return $ocLazyLoad.load([
                                // 'scripts/controllers/table.controller.js'


                            ])
                        }]
                    }
                })

        }])
    .run();
