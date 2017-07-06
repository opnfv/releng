'use strict';

/**
 * get data factory
 */
angular.module('opnfvApp')
    .factory('TableFactory', function($resource, $rootScope, $http) {

        var BASE_URL = 'http://testresults.opnfv.org/reporting2';
        $.ajax({
          url: 'config.json',
          async: false,
          dataType: 'json',
          success: function (response) {
              BASE_URL = response.url;
          },
          error: function (response){
              alert('fail to get api url, using default: http://testresults.opnfv.org/reporting2')
          }
        });

        return {
            getFilter: function() {
                return $resource(BASE_URL + '/landing-page/filters', {}, {
                    'get': {
                        method: 'GET',

                    }
                });
            },
            getScenario: function() {

                var config = {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                    }
                }

                return $http.post(BASE_URL + '/landing-page/scenarios', {}, config);
            },


            getProjectUrl: function() {
                return $resource(BASE_URL + '/projects-page/projects', {}, {
                    'get': {
                        method: 'GET'
                    }
                })
            },
            getProjectTestCases: function(name) {
                var config = {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                    }
                };
                return $http.get(BASE_URL + '/projects/' + name + '/cases', {}, config)


            },
            getProjectTestCaseDetail: function() {
                return $resource(BASE_URL + '/projects/:project/cases/:testcase', { project: '@project', testcase: '@testcase' }, {
                    'get': {

                        method: 'GET'
                    }
                })
            }

        };
    });
