
/*--------loader script-----------*/
$(document).ready(function(){


    var post_form = document.getElementById('post_form');   
    var count = 0;
    //var quiz_form = document.getElementById('quiz_form');
    var rows = $(post_form).find('div.row');

    $(document.body).on('click', "div.start_task", function (e) {
        var prolog = document.getElementById('prolog');
        $(prolog).hide();

        // show current row
        var curr = $(rows).get(count);
        $(curr).show();
    })

   
	
    var num_posts = window.num_posts || null;
   // var num_labeled = window.num_labeled || null;
   // var d = parseFloat({{ num_labeled }}/{{ num_posts }})*100;


   
    $(document.body).on('click',"label.element-animation", function (e) {
	count++;        
	$(this).closest('.row').delay(100).fadeOut();
        $(this).closest('.row').promise().done(function() {
//            $(post_form).submit()		
	  //}
	
	var curr = $(rows).get(count);
        $(curr).show();
	
        });
	
	 if(count >= num_posts) {
            console.log("complete");
            $('input[type=radio]').on('change', function() {
		var elem = document.getElementById('myBar');   
		  var widthP =parseInt(elem.style.width,10);
		  //document.write(parseInt(elem.style.width,10));
		  //var id =frame();
		    if (isNaN(widthP)){
			widthP = 1;
			elem.style.width = widthP + '%'; 
			elem.innerHTML = widthP + '%';
			//document.write(elem.style.width);
		    }
	
		    if (widthP >= 100) {
		      //clearInterval(id);
		    } else {			
		      widthP = widthP; 
		      elem.style.width = widthP + '%'; 
		      elem.innerHTML = widthP;
		}
	  //update amount label when value changes
		//$("#amount").text($("#progress").progressbar("option", "value") + "%");		
                $(this).closest("form").submit();
            });
        }
    });
    
	 $(function() {
	    $("#progress").progressbar({ change: function() {
	 
	    //update amount label when value changes
	    $("#amount").text($("#progress").progressbar("option", "value") + "%");
	  } });
	});

});	
