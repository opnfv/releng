/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    /** Main app module where application dependencies are listed. */
    angular
        .module('testapiApp', [
            'ui.router','ui.bootstrap', 'cgBusy',
            'ngResource', 'angular-confirm'
        ]);

    angular
        .module('testapiApp')
        .config(configureRoutes);

    configureRoutes.$inject = ['$stateProvider', '$urlRouterProvider'];

    /**
     * Handle application routing. Specific templates and controllers will be
     * used based on the URL route.
     */
    function configureRoutes($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/');
        $stateProvider.
            state('home', {
                url: '/',
                templateUrl: 'testapi-ui/components/home/home.html'
            }).
            state('about', {
                url: '/about',
                templateUrl: 'testapi-ui/components/about/about.html'
            }).
            state('guidelines', {
                url: '/guidelines',
                templateUrl: 'testapi-ui/components/guidelines/guidelines.html',
                controller: 'GuidelinesController as ctrl'
            }).
            state('communityResults', {
                url: '/community_results',
                templateUrl: 'testapi-ui/components/results/results.html',
                controller: 'ResultsController as ctrl'
            }).
            state('userResults', {
                url: '/user_results',
                templateUrl: 'testapi-ui/components/results/results.html',
                controller: 'ResultsController as ctrl'
            }).
            state('resultsDetail', {
                url: '/results/:testID',
                templateUrl: 'testapi-ui/components/results-report' +
                             '/resultsReport.html',
                controller: 'ResultsReportController as ctrl'
            }).
            state('profile', {
                url: '/profile',
                templateUrl: 'testapi-ui/components/profile/profile.html',
                controller: 'ProfileController as ctrl'
            }).
            state('authFailure', {
                url: '/auth_failure',
                templateUrl: 'testapi-ui/components/home/home.html',
                controller: 'AuthFailureController as ctrl'
            }).
            state('logout', {
                url: '/logout',
                templateUrl: 'testapi-ui/components/logout/logout.html',
                controller: 'LogoutController as ctrl'
            }).
            state('userVendors', {
                url: '/user_vendors',
                templateUrl: '/testapi-ui/components/vendors/vendors.html',
                controller: 'VendorsController as ctrl'
            }).
            state('publicVendors', {
                url: '/public_vendors',
                templateUrl: '/testapi-ui/components/vendors/vendors.html',
                controller: 'VendorsController as ctrl'
            }).
            state('vendor', {
                url: '/vendor/:vendorID',
                templateUrl: '/swagger/testapi-ui/components/vendors/vendor.html',
                controller: 'VendorController as ctrl'
            }).
            state('userProducts', {
                url: '/user_products',
                templateUrl: '/testapi-ui/components/products/products.html',
                controller: 'ProductsController as ctrl'
            }).
            state('publicProducts', {
                url: '/public_products',
                templateUrl: '/testapi-ui/components/products/products.html',
                controller: 'ProductsController as ctrl'
            }).
            state('cloud', {
                url: '/cloud/:id',
                templateUrl: '/testapi-ui/components/products/cloud.html',
                controller: 'ProductController as ctrl'
            }).
            state('distro', {
                url: '/distro/:id',
                templateUrl: '/testapi-ui/components/products/distro.html',
                controller: 'ProductController as ctrl'
            });
    }

    angular
        .module('testapiApp')
        .config(disableHttpCache);

    disableHttpCache.$inject = ['$httpProvider'];

    /**
     * Disable caching in $http requests. This is primarily for IE, as it
     * tends to cache Angular IE requests.
     */
    function disableHttpCache($httpProvider) {
        if (!$httpProvider.defaults.headers.get) {
            $httpProvider.defaults.headers.get = {};
        }
        $httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
        $httpProvider.defaults.headers.get.Pragma = 'no-cache';
    }

    angular
        .module('testapiApp')
        .run(setup);

    setup.$inject = [
        '$http', '$rootScope', '$window', '$state', 'testapiApiUrl'
    ];

    /**
     * Set up the app with injections into $rootscope. This is mainly for auth
     * functions.
     */
    function setup($http, $rootScope, $window, $state, testapiApiUrl) {

        $rootScope.auth = {};
        $rootScope.auth.doSignIn = doSignIn;
        $rootScope.auth.doSignOut = doSignOut;
        $rootScope.auth.doSignCheck = doSignCheck;

        var sign_in_url = testapiApiUrl + '/auth/signin';
        var sign_out_url = testapiApiUrl + '/auth/signout';
        var profile_url = testapiApiUrl + '/profile';

        /** This function initiates a sign in. */
        function doSignIn() {
            $window.location.href = sign_in_url;
        }

        /** This function will initate a sign out. */
        function doSignOut() {
            $rootScope.auth.currentUser = null;
            $rootScope.auth.isAuthenticated = false;
            $window.location.href = sign_out_url;
        }

        /**
         * This function checks to see if a user is logged in and
         * authenticated.
         */
        function doSignCheck() {
            return $http.get(profile_url, {withCredentials: true}).
                success(function (data) {
                    $rootScope.auth.currentUser = data;
                    $rootScope.auth.isAuthenticated = true;
                }).
                error(function () {
                    $rootScope.auth.currentUser = null;
                    $rootScope.auth.isAuthenticated = false;
                });
        }

        $rootScope.auth.doSignCheck();
    }

    angular
        .element(document)
        .ready(loadConfig);

    /**
     * Load config and start up the angular application.
     */
    function loadConfig() {

        var $http = angular.injector(['ng']).get('$http');

        /**
         * Store config variables as constants, and start the app.
         */
        function startApp(config) {
            // Add config options as constants.
            angular.forEach(config, function(value, key) {
                angular.module('testapiApp').constant(key, value);
            });

            angular.bootstrap(document, ['testapiApp']);
        }

        $http.get('testapi-ui/config.json').success(function (data) {
            startApp(data);
        }).error(function () {
            startApp({});
        });
    }
})();
