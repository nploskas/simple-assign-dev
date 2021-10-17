
function on_order_open(order_id) {
    var url=window.location.href;
    var x=document.getElementsByClassName("order_list_url");
    var i;
    for (i = 0; i < x.length; i++) {
        x[i].setAttribute("value", url);
    }
    document.getElementById(order_id).submit();
}
