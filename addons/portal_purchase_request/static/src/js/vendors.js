odoo.define('portal_purchase_request.order_request', function (require) {
'use strict';
  var ajax = require('web.ajax');
      $(document).ready(function() {
        var subtotal = 0 ;
        var qty = 1 ;
        var price= 0 ;
        var tax_percentage = 0 ;
        var total = 0 ;

        /*  Validation File Size */
     $("#upload_file").on("change", function () {
     if(this.files[0].size > 5000000) {
       alert("Please upload file less than 5MB. Thanks!!");
       $(this).val('');
     }
    });


         $('#qty').on('input', function() {
         var tax = 0
         qty=$('#qty').val();
         subtotal =parseFloat( $('#unit_price').val() )* parseFloat(qty)
          $('#subtotal').text(subtotal);
         tax= parseFloat($('#subtotal').text() ) / 100 * tax_percentage
          $('#tax').text(tax);
          $('#total').text(tax+subtotal);
        });

         $('#product').on('change', function(){
                    $('.table_vendor').css('display','table');
                    $('#subtotal_price').css('display','block');
                    $("#vendors_select").attr("required", true);

                    $('#vendors_select').empty()
                    var array_childs =[];
                    var array_taxes =[];
                     var last_product = $("option:selected:last",this).val();
                     var qty = $("#qty").val();

                    if (last_product) {

                    ajax.jsonRpc("/get_vendors_list", 'call', {
                    'product_id' :last_product,
                    'qty' :qty,
                     })
                    .then(function (data) {
                        /*  Taxes */
                        array_taxes = data['taxes']
                        tax_percentage = parseFloat(array_taxes)
                        array_childs = data['vendors']
                        var table = document.getElementById("vendor_list");
                        var option = '';

                        for (var i = 0; i < array_childs.length; i++) {
                          /*  Select Vendors Prices  */
                        $('#vendors_select').append($('<option>', {
                        value: array_childs[i][0],
                        text: array_childs[i][2],
                            }));
                         /* Table Vendors Informations  */
                        option += '<tr>'+
                         '<td>'+ array_childs[i][1]+'</td>'+
                         '<td>'+ array_childs[i][2]+'</td>'+
                         '</tr>';
                                 }
                    table.innerHTML=option;

                });
                    }
                    else {
                    $('.table_vendor').css('display','none');

                    }

                  });

         $('#vendors_select').on('change', function(){
          price = $("option:selected:last",this).text();
          $('#unit_price').val(price);

          $('#subtotal').text(parseFloat( price ) * parseFloat(qty));
           $('#tax').text(   parseFloat($('#subtotal').text() ) / 100 * tax_percentage);
           $('#total').text( parseFloat($('#subtotal').text() ) / 100 * tax_percentage + parseFloat( price ) * parseFloat(qty));



         });

        /* Accept Order */
        $("#accepter_order" ).click(function() {
          var order_id=$("#order_id").val();
          ajax.jsonRpc("/accept_order", 'call', {
                'order_id' :order_id,
                 })
                .then(function (data) {
                  $("#st1").addClass('active')
                   $('#accepter_order').css('display','none');
                   $('#reject_order').css('display','none');
            });
                });

            /* Reject Order */
        $("#reject_order" ).click(function() {
            var order_id=$("#order_id").val();
            ajax.jsonRpc("/reject_order", 'call', {
                'order_id' :order_id,
                 })
                .then(function (data) {
                  $('#reject_order').css('display','none');
                    $('#accepter_order').css('display','none');
                 $("#progressbar li.active:before, #progressbar li.active:after").css('background','red');

            });
                });

         /* Buy Product  */
        $("#buy_product" ).click(function() {
            var order_id=$("#order_id").val();
                ajax.jsonRpc("/buy_product", 'call', {
                    'order_id' :order_id,
                     })
                    .then(function (data) {
                       $("#st2").addClass('active')
                        $('#buy_product').css('display','none');
                });
                });
       });

   });
