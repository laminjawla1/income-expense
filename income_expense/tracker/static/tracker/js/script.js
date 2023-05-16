$(document).ready(function(){
    $('#div_id_item_four, #div_id_item_four_quantity, #div_id_item_four_unit_price, #div_id_item_four_total_price, #div_id_item_four, #div_id_item_five, #div_id_item_five_quantity, #div_id_item_five_unit_price, #div_id_item_five_total_price, #div_id_item_six, #div_id_item_six_quantity, #div_id_item_six_unit_price, #div_id_item_six_total_price, #div_id_item_seven, #div_id_item_seven_quantity, #div_id_item_seven_unit_price, #div_id_item_seven_total_price, #div_id_item_eight, #div_id_item_eight_quantity, #div_id_item_eight_unit_price, #div_id_item_eight_total_price, #div_id_item_nine, #div_id_item_nine_quantity, #div_id_item_nine_unit_price, #div_id_item_nine_total_price, #div_id_item_ten, #div_id_item_ten_quantity, #div_id_item_ten_unit_price, #div_id_item_ten_total_price').hide()

    $('#more-line').click(function(){
        $('#div_id_item_four, #div_id_item_four_quantity, #div_id_item_four_unit_price, #div_id_item_four_total_price, #div_id_item_four').slideToggle(300)
        $('#div_id_item_five, #div_id_item_five_quantity, #div_id_item_five_unit_price, #div_id_item_five_total_price').slideToggle(300)
        $('#div_id_item_six, #div_id_item_six_quantity, #div_id_item_six_unit_price, #div_id_item_six_total_price').slideToggle(300)
        $('#div_id_item_seven, #div_id_item_seven_quantity, #div_id_item_seven_unit_price, #div_id_item_seven_total_price').slideToggle(300)
        $('#div_id_item_eight, #div_id_item_eight_quantity, #div_id_item_eight_unit_price, #div_id_item_eight_total_price').slideToggle(300)
        $('#div_id_item_nine, #div_id_item_nine_quantity, #div_id_item_nine_unit_price, #div_id_item_nine_total_price').slideToggle(300)
        $('#div_id_item_ten, #div_id_item_ten_quantity, #div_id_item_ten_unit_price, #div_id_item_ten_total_price').slideToggle(300)
    });

    $('#id_item_one_quantity, #id_item_one_unit_price, #id_item_two_quantity, #id_item_two_unit_price, #id_item_three_quantity, #id_item_three_unit_price, #id_item_four_quantity, #id_item_four_unit_price, #id_item_five_quantity, #id_item_five_unit_price, #id_item_six_quantity, #id_item_six_unit_price, #id_item_seven_quantity, #id_item_seven_unit_price, #id_item_eight_quantity, #id_item_eight_unit_price #id_item_nine_quantity, #id_item_nine_unit_price, #id_item_ten_quantity, #id_item_ten_unit_price').keyup(function(){
        var item_one_quantity_text = $('#id_item_one_quantity').val();
        var item_one_unit_price_text = $('#id_item_one_unit_price').val();
        var item_one_total = item_one_quantity_text * item_one_unit_price_text
    
        var item_two_quantity_text = $('#id_item_two_quantity').val();
        var item_two_unit_price_text = $('#id_item_two_unit_price').val();
        var item_two_total = item_two_quantity_text * item_two_unit_price_text
    
        var item_three_quantity_text = $('#id_item_three_quantity').val();
        var item_three_unit_price_text = $('#id_item_three_unit_price').val();
        var item_three_total = item_three_quantity_text * item_three_unit_price_text
        
        var item_four_quantity_text = $('#id_item_four_quantity').val();
        var item_four_unit_price_text = $('#id_item_four_unit_price').val();
        var item_four_total = item_four_quantity_text * item_four_unit_price_text
    
        var item_five_quantity_text = $('#id_item_five_quantity').val();
        var item_five_unit_price_text = $('#id_item_five_unit_price').val();
        var item_five_total = item_five_quantity_text * item_five_unit_price_text
    
        var item_six_quantity_text = $('#id_item_six_quantity').val();
        var item_six_unit_price_text = $('#id_item_six_unit_price').val();
        var item_six_total = item_six_quantity_text * item_six_unit_price_text
    
        var item_seven_quantity_text = $('#id_item_seven_quantity').val();
        var item_seven_unit_price_text = $('#id_item_seven_unit_price').val();
        var item_seven_total = item_seven_quantity_text * item_seven_unit_price_text
    
        var item_eight_quantity_text = $('#id_item_eight_quantity').val();
        var item_eight_unit_price_text = $('#id_item_eight_unit_price').val();
        var item_eight_total = item_eight_quantity_text * item_eight_unit_price_text
    
        var item_nine_quantity_text = $('#id_item_nine_quantity').val();
        var item_nine_unit_price_text = $('#id_item_nine_unit_price').val();
        var item_nine_total = item_nine_quantity_text * item_nine_unit_price_text
    
        var item_ten_quantity_text = $('#id_item_ten_quantity').val();
        var item_ten_unit_price_text = $('#id_item_ten_unit_price').val();
        var item_ten_total = item_ten_quantity_text * item_ten_unit_price_text
    
        var total = item_one_total + item_two_total + item_three_total + item_four_total + item_five_total+ item_six_total + item_seven_total + item_eight_total + item_nine_total + item_ten_total
    
        $('#id_item_one_total_price').val(item_one_total);
        $('#id_item_two_total_price').val(item_two_total);
        $('#id_item_three_total_price').val(item_three_total);
        $('#id_item_four_total_price').val(item_four_total);
        $('#id_item_five_total_price').val(item_five_total);
        $('#id_item_six_total_price').val(item_six_total);
        $('#id_item_seven_total_price').val(item_seven_total);
        $('#id_item_eight_total_price').val(item_eight_total);
        $('#id_item_nine_total_price').val(item_nine_total);
        $('#id_item_ten_total_price').val(item_ten_total);
        $('#id_total_amount').val(total);
    });

      // Scroll Top Script
   //Check to see if the window is top if not then display button
   $(window).scroll(function(){
        if ($(this).scrollTop() > 50) {
        $('.scrollToTop').fadeIn();
        } else {
        $('.scrollToTop').fadeOut();
        }
    });

    //Click event to scroll to top
    $('.scrollToTop').click(function(){
        $('html, body').animate({scrollTop : 0},500);
        return false;
      });
     //END Scroll Top Script


});