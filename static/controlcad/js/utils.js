// js/utils/utils.js
// Utility functions for ControlCAD.

var utils = utils || {};

(function () {
    'use strict';

    utils = {

        // Obtain the csrf token cookie using jQuery
        getCookie: function (name) {

            var cookieValue = null;

            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        // Check if the supplied method require csrf protection
        csrfSafeMethod: function (method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        },

        // Test that a given url is a same-origin URL
        // `url` could be relative or scheme relative or absolute
        sameOrigin: function (url) {
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
                (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        },

        // Ajax default setup
        prepareAjax: function (csrftoken) {
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!utils.csrfSafeMethod(settings.type) && utils.sameOrigin(settings.url)) {
                        // Send the token to same-origin, relative URL only.
                        // Send the token only if the method warrants CSRF protection
                        // Using the CSRFToken value acquired earlier
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        },

        // Validation functions used to validate strings
        validateString: function (string) {
            // Only alphanumeric characters allowed and hyphen.
            return (/^[0-9\-A-Za-z]+$/.test(string));
        },
        spanishValidation: function (string) {
           // validateString + acute letters + ñ + Ñ
           // Á - u00C1    á - u00E1   ñ - u00F1
           // É - u00C9    é - u00E9   Ñ - u00D1
           // Í - u00CD    í - u00ED
           // Ó - u00D3    ó - u00F3
           // Ú - u00DA    ú - u00FA
           return (/^[0-9\-A-Za-z\u00C1\u00C9\u00CD\u00D3\u00DA\u00E1\u00E9\u00ED\u00F3\u00FA\u00F1\u00D1]+$/.test(string));
        }
    };

})();