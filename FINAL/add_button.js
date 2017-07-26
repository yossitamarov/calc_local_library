var room = 1;
function if_fields() {
 
    room++;
    var objTo = document.getElementById('if_fields')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room);
	var rdiv = 'removeclass'+room;
    divtest.innerHTML = '<div class="col-sm-2 nopadding"><div class="form-group"><h6>#'+room+'</h6></div></div> <div class="col-sm-9 nopadding"><div class="form-group"><input type="text" class="form-control" name="strategies_constraint_'+room+'" value="" placeholder="Constraint"></div></div><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields('+ room +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields(rid) {
	   $('.removeclass'+rid).remove();
   }
   
var room2 = 1;
function if_fields_payment() {
 
    room2++;
    var objTo = document.getElementById('if_fields_payment')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room2);
	var rdiv = 'removeclass'+room2;
    divtest.innerHTML = '<div class="col-sm-2 nopadding"><div class="form-group"><h6>#'+room2+'</h6></div></div><div class="col-sm-9 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="payment_if_cond_'+room2+'" value="" placeholder="if"></div></div><!--<div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_true" name="payment_if_true_'+room2+'" value="" placeholder="then">    </div></div><div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_false" name="payment_if_false_'+room2+'" value="" placeholder="else">    </div></div>--><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_payment('+ room2 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_payment(rid) {
	   $('.removeclass'+rid).remove();
   }
var room3 = 1;
function if_fields_dimension_rows_cond() {
 
    room3++;
    var objTo = document.getElementById('if_fields_dimension_rows_cond')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room3);
	var rdiv = 'removeclass'+room3;
    divtest.innerHTML = '<div class="col-sm-3 nopadding"><div class="form-group"><h6>#'+room3+'</h6></div></div><div class="col-sm-8 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="dimensions_column_if_cond_'+room3+'" value="" placeholder="if"></div></div><!--<div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_true" name="dimensions_column_if_true_'+room3+'" value="" placeholder="then">    </div></div><div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_false" name="dimensions_column_if_false_'+room3+'" value="" placeholder="else">    </div></div>--><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_dimension_columns_cond('+ room3 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_dimension_rows_cond(rid) {
	   $('.removeclass'+rid).remove();
   }   
var room4 = 1;
function if_fields_dimension_rows_names() {
	
    room4++;
    var objTo = document.getElementById('if_fields_dimension_rows_names')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room4);
	var rdiv = 'removeclass'+room4;
    divtest.innerHTML = '<div class="col-sm-3 nopadding"><div class="form-group"><h6>#'+room4+'</h6></div></div> <div class="col-sm-8 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="dimensions_row_category_name_'+room4+'" value="" placeholder="Category Name"></div></div><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_dimension_rows_names('+ room4 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_dimension_rows_names(rid) {
	   $('.removeclass'+rid).remove();
   } 
var room5 = 1;
function if_fields_dimension_columns_cond() {
 
    room5++;
    var objTo = document.getElementById('if_fields_dimension_columns_cond')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room5);
	var rdiv = 'removeclass'+room5;
    divtest.innerHTML = '<div class="col-sm-3 nopadding"><div class="form-group"><h6>#'+room5+'</h6></div></div><div class="col-sm-8 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="dimensions_column_if_cond_'+room5+'" value="" placeholder="if"></div></div><!--<div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_true" name="dimensions_column_if_true_'+room5+'" value="" placeholder="then">    </div></div><div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_false" name="dimensions_column_if_false_'+room5+'" value="" placeholder="else">    </div></div>--><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_dimension_columns_cond('+ room5 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_dimension_columns_cond(rid) {
	   $('.removeclass'+rid).remove();
   }   
var room6 = 1;
function if_fields_dimension_columns_names() {
 
    room6++;
    var objTo = document.getElementById('if_fields_dimension_columns_names')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room6);
	var rdiv = 'removeclass'+room6;
    divtest.innerHTML = '<div class="col-sm-3 nopadding"><div class="form-group"><h6>#'+room6+'</h6></div></div> <div class="col-sm-8 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="dimensions_column_category_name_'+room6+'" value="" placeholder="Category Name"></div></div><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_dimension_columns_names('+ room6 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_dimension_columns_names(rid) {
	   $('.removeclass'+rid).remove();
   } 
var room7 = 1;
function if_fields_strategies_vectors() {
 
    room7++;
    var objTo = document.getElementById('if_fields_strategies_vectors')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room7);
	var rdiv = 'removeclass'+room7;
    divtest.innerHTML = '<div class="col-sm-2 nopadding"><div class="form-group"><h6>#'+room7+'</h6></div></div><div class="col-sm-9 nopadding"><div class="form-group"><input type="text" class="form-control" id="if_cond" name="strategies_vector_'+room7+'" value="" placeholder="Strategy Vector"></div></div><!--<div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_true" name="payment_if_true_'+room2+'" value="" placeholder="then">    </div></div><div class="col-sm-3 nopadding">    <div class="form-group">        <input type="text" class="form-control" id="if_false" name="payment_if_false_'+room2+'" value="" placeholder="else">    </div></div>--><div class="col-sm-1 nopadding">    <div class="form-group">        <div class="input-group">            <div class="input-group-btn">                <button class="btn btn-danger" type="button" onclick="remove_if_fields_strategies_vectors('+ room7 +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button>            </div>        </div>    </div></div><div class="clear"></div>';
    
    objTo.appendChild(divtest)
}
   function remove_if_fields_strategies_vectors(rid) {
	   $('.removeclass'+rid).remove();
   }
   