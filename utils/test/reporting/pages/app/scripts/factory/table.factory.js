'use strict';

/**
 * get data factory
 */
angular.module('opnfvApp')
    .factory('TableFactory', function ($resource, $rootScope) {
        // var baseUrl = base_Url;

        return {
            getFilter: function () {
                return $resource(baseUrl + '/', {}, {
                    'post': {
                        method: 'POST',

                    }
                });
            }
        };
    });
