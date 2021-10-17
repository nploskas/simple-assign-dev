

function isChild (obj,parentObj){
    while (obj != undefined && obj != null && obj.tagName.toUpperCase() != 'BODY'){
        if (obj == parentObj){
            return true;
        }
        obj = obj.parentNode;
    }
    return false;
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev, el) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
//    if (!isChild(document.getElementById(data), el)) { el.appendChild(document.getElementById(data)); }
    el.appendChild(document.getElementById(data));
    var target_width = el.offsetWidth;
    var n_time_window = Math.floor((ev.offsetX/target_width)*12);
    start = $j("#target_start_data").data("tt");
    document.getElementById(data).style.left = (target_width/12)*(n_time_window-start+1) + "px";
    var save_bt = document.getElementById("save");
    save_bt.setAttribute("class", "btn btn-primary");
    save_bt.removeAttribute("disabled");
}


function my_onclick(ev) {
    var existing = $j("#existing_data").data("tt");
    if ((!document.getElementById("new")) && (existing=='False') && (ev.target.className == "chart-row-bars") ) {
        $j( function() {
            var default_task_duration = $j("#target_dd_data").data("tt");
            var task_type = $j("#target_type_data").data("tt");
            var order_id = $j("#target_order_id_data").data("tt");
            var task = document.createElement("LI");
            var save_bt = document.getElementById("save");
            task.setAttribute("class", "chart-li-one");
            task.innerText = task_type+", "+"Ord.ID: " + order_id;
            task.style.backgroundColor = '#f0ad4e';
            ev.target.appendChild(task);
            task.setAttribute("draggable", "true");
            task.setAttribute("ondragstart", "drag(event)");
            task.setAttribute("id", "new");
            $j('[data-toggle="tooltip"]').tooltip('disable');
            resize_step = document.getElementsByClassName('chart-row-bars')[0].offsetWidth/12;
            $j( "#new" ).resizable({handles: 'e'}, {grid: [resize_step, 1]},  {minWidth: 2*resize_step}, {resize: function( event, ui ){
                        var save_bt = document.getElementById("save");
                        save_bt.setAttribute("class", "btn btn-primary");
                        document.getElementById("save_bt").disabled = false;
                        }}
            );
            var target_width = ev.target.offsetWidth;
            var n_time_window = Math.round((ev.offsetX/target_width)*12);
            task.style.left = (target_width/12)*n_time_window + "px";
            task.style.width = (target_width/12)*default_task_duration + "px";
            document.getElementById("target_start_data").setAttribute("data-tt", "1");
            save_bt.setAttribute("class", "btn btn-primary");
            save_bt.removeAttribute("disabled");
;
        });
    }
}

function save_scheduling() {
    var task=document.getElementById("new");
    if (task) {
        var task_id = $j("#target_task_id_data").data("tt");
        var task_duration=task.offsetWidth;
        var workday_width=task.parentElement.offsetWidth;
        var start_time_int=Math.round(task.offsetLeft/(workday_width/12))-3;
        var end_time_int=start_time_int+Math.round(task_duration/(workday_width/12))
        var save_bt = document.getElementById("save");
        var user_email = task.parentNode.id;
        document.getElementById("task_id").value=task_id;
        document.getElementById("date").value=document.getElementById("datepicker").value;
        document.getElementById("start_time_index").value=start_time_int;
        document.getElementById("end_time_index").value=end_time_int;
        document.getElementById("user_email").value=user_email;
        document.getElementById("form_out").submit();
        }
}

function cancel_scheduling() {
    document.getElementById("form_out").submit();
}


var $j = jQuery.noConflict();

$j( function() {
    $j( "#datepicker" ).datepicker({dateFormat: 'yy-mm-dd'});
});

$j( function() {
    $j("#datepicker").change(function(){
        document.getElementById("form_date").submit();
    });
});

$j(function () {
  var existing = $j("#existing_data").data("tt");
  if (existing=='False') {
    var x = document.getElementsByClassName('chart-row-bars');
    var i;
    for (i = 0; i < x.length; i++) {
        x[i].title = "Click to drop task";
    }
    $j('[data-toggle="tooltip"]').tooltip({
        position: { my: "left+15 center", at: "right-50 center" }
    });
   }
})

$j( function() {
    resize_step = document.getElementsByClassName('chart-row-bars')[0].offsetWidth/12;
    $j( "#new" ).resizable({handles: 'e'}, {grid: [resize_step, 1]},  {minWidth: 2*resize_step}, {resize: function( event, ui ){
        var save_bt = document.getElementById("save");
        save_bt.setAttribute("class", "btn btn-primary");
        save_bt.removeAttribute("disabled");
    }}
    )
}) ;


