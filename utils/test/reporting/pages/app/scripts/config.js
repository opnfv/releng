/**
 * @ngdoc overview
 * @name opnfvApp
 * @description
 * # opnfvApp
 *
 * Main config file of the application.
 */
angular
    .module('opnfvApp').config(['$httpProvider', '$qProvider', function($httpProvider, $qProvider) {

            $httpProvider.defaults.useXDomain = true;
            delete $httpProvider.defaults.headers.common['X-Requested-With'];

            $qProvider.errorOnUnhandledRejections(false);

        }

    ]);