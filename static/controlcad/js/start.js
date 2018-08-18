// start.js
// Used in the `start` page only for DOM manipulation.
// This script affects only the presentation layer.

(function () {
    'use strict';

    // Stop the carousel. Only move when click events
    // get fired.
    $('.carousel').carousel('pause');

    // Set OnClick events for links. On each link:
    // * Mark current link as active (the others must be set to inactive)
    // * Move carousel to exact position.
    $('#draws-link').click(function () {
        $('li[id*="item"]').removeAttr('class');
        $('#draws-item').addClass('active');
        $('#cover-carousel').carousel(0);
    });
    $('#projects-link').click(function () {
        $('li[id*="item"]').removeAttr('class');
        $('#projects-item').addClass('active');
        $('#cover-carousel').carousel(1);
    });
    $('#tasks-link').click(function () {
        $('li[id*="item"]').removeAttr('class');
        $('#tasks-item').addClass('active');
        $('#cover-carousel').carousel(2);
    });
})();
