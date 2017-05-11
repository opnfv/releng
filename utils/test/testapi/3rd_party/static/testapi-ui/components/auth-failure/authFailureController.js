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

    angular
        .module('testapiApp')
        .controller('AuthFailureController', AuthFailureController);

    AuthFailureController.$inject = ['$location', '$state', 'raiseAlert'];
    /**
     * TestAPI Auth Failure Controller
     * This controller handles messages from TestAPI API if user auth fails.
     */
    function AuthFailureController($location, $state, raiseAlert) {
        var ctrl = this;
        ctrl.message = $location.search().message;
        raiseAlert('danger', 'Authentication Failure:', ctrl.message);
        $state.go('home');
    }
})();
