
/*--------loader script-----------*/
$(document).ready(function(){

    var count = 0;
    var quiz_form = document.getElementById('quiz_form');
    var rows = $(quiz_form).find('div.row');
    $(document.body).on('click', "div.start_quiz", function (e) {
        var prolog = document.getElementById('prolog');
        $(prolog).hide();	
        // show current row
        var curr = $(rows).get(count);
        $(curr).show();
    })

    var num_posts = window.num_posts || null;
    
    $(document.body).on('click',"label.element-animation",function (e) {
        count++;
        $(this).closest('.row').delay(100).fadeOut();
        $(this).closest('.row').promise().done(function() {
            curr = $(rows).get(count);
            $(curr).show();
        });

        if(count >= num_posts) {
            console.log("complete");
            $('input[type=radio]').on('change', function() {
                $(this).closest("form").submit();
            });
        }
    });
});	
