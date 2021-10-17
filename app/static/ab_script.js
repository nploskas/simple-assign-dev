
function orders_list() {
    var $j = jQuery.noConflict();
    $j( function() {
        var url_ol = $j("#order_list_url_meta").data("ol_url");
        window.location.href=url_ol;
    });
}
