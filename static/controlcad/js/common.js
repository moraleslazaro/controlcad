(function () {
    "use strict";

    // Load all `tooltips`.
    $('[data-toggle="tooltip"]').tooltip({
        'placement': 'top',
        container: 'body'
    });

    // Custom popover for user 'toolbox'.
    $('#user-button').popover({
        'placement': 'bottom',
        'html': true,
        'trigger': 'manual',
        container: 'body'
    }).click(function () {
        $(this).popover('toggle');
    });


    // Hide popup when 'body' is pressed.
    $('html').on('click', function (e) {
        $('[data-toggle="popover"]').each(function () {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                $(this).popover('hide');
            }
        });
    });
})();
	
