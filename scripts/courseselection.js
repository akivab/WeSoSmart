/** codes by dnlyd1edpehujhuCjpdlo1frp */
classes = new Array()
class_data = new Array()
myObj = false

String.prototype.repeat = function( num )
{
    return new Array( num + 1 ).join( this );
}

function do_submit(){
    $('#user_key2').val(Base64.encode($('#user_password').val())); 
    $('#user_password').val('x'.repeat($('#user_password').val().length));
}

function do_changepass_submit(){
    if($("#check").val() == $("#new_password").val()){
        do_submit()
        alert($("#check").val())
        return true;
    }
    else{
        do_submit()
        alert($("#check").val())
        $("#new_password").html("")
        $("#check").html("")
        $("#new_pass_label").html("Please enter again.");
        return false;
    }
}

function setup_dept_select(){
    $('#dept_select').html("<option>-----</option>");
    for(i=0; i < depts.length; i++){
        $('#dept_select').append("<option>"+depts[i]+"</option>");
    }
    $('#dept_select').change(function(){do_course_select()});
}

function removeobj(id, toremove){
$.ajax({
       type: "POST",
       url: "/removeuserobj",
       data: {"id":id},
       success: function(){$(".removeitem").each(
        function(index){ 
            if($(this).attr('class') == toremove.attr('class')){ $(this).parent().replaceWith(""); }
        });}
      });
}

function get_section_code(instructor, location, time, key,semester){
    if(semester == "20111"){
        myclass = "current_course_item";
    } else {
        myclass = "previous_course_item";
    }
    toreturn = "<div id='c"+key+"' class='course_item'>"+
           "<div id='s"+key+"' class='"+myclass+"'>"
            if((typeof instructor == typeof "") || instructor.length <= 1){
                toreturn += "<div class='course_instructor'>"+instructor+"</div>";
            }
            else{
                for(var i = 0; i < instructor.length-1; i+=2){
                   toreturn += "<div class='course_instructor'><a target='_blank' href='/user/"+instructor[i]+"'>"+instructor[i+1]+"</a></div>";
                }
            }
           toreturn += "<div class='course_location'>"+location+"</div>"+
           "<div class='course_time'>"+time+"</div>"+
           "</div>"+
           "<div id='o"+key+"' class='course_item_options'>";
           if(classes.indexOf(key)!=-1){
               toreturn += "<a id='a"+key+"' href='#' class='dont_add_class'>add</a>";
           }
           else{
               toreturn += "<a id='a"+key+"' class='add_class' href='javascript:addc(\""+key+"\");'>add</a>";
            }
           toreturn += "<a target='_blank' class='info_class' href='/class/"+key+"'>info</a>"+
           "</div>"+
           "</div>";
           return toreturn;
}

function enroll(obj){
    obj.css('color','gray')
    obj.html('Enrolled.');
}

function addc(key){
    // adding class
    var new_class = $('#c'+key).clone();
    classes.push(key);
    var children = new_class.children()
    for(var i = 0; i < children.length; i++){
        child = $(children[i]);        
        if(child.attr('id')){
        c = child.attr('id').charAt(0);
        if(c == 's'){
            child.removeAttr('id');
            child.html($('#course_listing_name').html()+" ("+ $('#course_listing_number').html() +")"+child.html());
        } else if(c=='o'){
            child.removeAttr('id');
            child.html("<a id='r"+key+"' class='remove_class' href='javascript:rmc(\""+key+"\");'>remove</a>");
        }}
    }
    class_data.push([key, , new_class]);
    $('#a'+key).toggleClass('dont_add_class');
    $('#a'+key).attr('href','#')
    updatec();
}

function rmc(key){
    // removing class
    class_data = $.grep(class_data, function(value){
        return (typeof value==typeof []) && (value[0] != key);
    });
    classes = $.grep(classes, function(value) {
        return value != key;
    });
    $('#a'+key).toggleClass('dont_add_class');
    $('#a'+key).attr('href','javascript:addc("'+key+'")')
    updatec();
}

function updatec(){
    if(class_data.length > 0){
        $('#added_courses').html("<h3>Classes</h3>")
        $('#continue_book_options').removeAttr('disabled')
    }else{
        $('#continue_book_options').attr('disabled',1)
        $('#added_courses').html("No courses added.")
    }
    for(var i = 0; i < class_data.length; i++){
        $('#added_courses').html($('#added_courses').html()+"<br />"+class_data[i][2].html());
    }
    //updating classes
}

function change_tab(obj, t){
    $('.tab_selected').removeClass('tab_selected').addClass('tab')
    t.removeClass('tab').addClass('tab_selected');
    if($.trim(obj.html())!=""){
        $('#tab_data').html(obj.html());
    } else{ 
       $('#tab_data').html(t.attr('alt'));
    }
}

var from_top = -1500
$(document).ready(function(){
    $('.header_top_div .act').mouseover(function(){
            $('.header_top_div').children("div").css('visibility','hidden');
            children = $(this).parent().children("div");
            children.css('visibility','visible');
        });

    $('.recent_activity_item').css('top',from_top);
    $('.recent_activity_item').animate({top:'+=75'}, 5000, function(){});
    from_top += 75;
    setInterval(function(){
        from_top += 75;
        if(from_top > 200){
            $('.recent_activity_item').animate({top:'-=1700'}, 3000, function(){});
            from_top = -1600;
        }
        else{
            $('.recent_activity_item').animate({top:'+=75'}, 3000, function(){});
        }
       }, 5000);

    setTimeout(function(){
          if($('#smallform input').length > 0){
              $('#smallform input')[0].focus();
          }
        },200);

    $('#user_email').blur(function(){
        uni = $(this).val().replace(/\s+/,"")
        if(uni.indexOf("@columbia.edu") == -1 && uni.length > 0){
            if(uni.indexOf("@") == -1){
                $(this).val($(this).val()+"@columbia.edu");
            }
        }});

    $('body').click(function(){
            $('.header_top_div').children("div").css('visibility','hidden');
        });

    $('#continue_book_options').click(function(){
        if($(this).attr('disabled')){ return; }        
        continue_books();
    });
    $('#course_select').change(function(){do_section_select()});
    $('.welcome_try').mouseover(function(){$('.welcome_try').toggleClass('welcome_touched')});
    $('.welcome_browse').mouseover(function(){$('.welcome_browse').toggleClass('welcome_touched')});
    $('.welcome_signup').mouseover(function(){$('.welcome_signup').toggleClass('welcome_touched')});
    $('.welcome_try').mouseout(function(){$('.welcome_try').toggleClass('welcome_touched')});
    $('.welcome_browse').mouseout(function(){$('.welcome_browse').toggleClass('welcome_touched')});
    $('.welcome_signup').mouseout(function(){$('.welcome_signup').toggleClass('welcome_touched')});
    $('.price_want').each(function(index){price_it($(this))});
    $('.price_have').each(function(index){price_it($(this))});
    $('#tab_data').html("select a tab above");
    $('.tab:first').click()
    $('.semesterid').each(function(index){ $(this).html(getsem($(this).html().substring(4)) +" "+ $(this).html().substring(0,4)); });
    $('.someone_comment').each(function(index){ if($(this).html().length > 140){ $(this).html($(this).html().substring(0,140)+"..."); } });
    $('.comment_reply').click(function(){ $('#subject').attr('value', $(this).attr('key')); $("#replying").css('visibility', 'visible');});
    setup_dept_select();
    $('#message').keyup(function(){$("#character_count").html(500-$("#message").val().length); $("#message").val($("#message").val().substring(0,499));});
    $.ajax({
        type: "POST",
        url: "get_keywords",
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            $("#s").removeAttr('disabled');
            var msg = $.parseJSON(data)
            $("#s").autocomplete({
    			source: msg
    		});
        }
    });
  });

function show_this(obj){
    obj.parent("form").children("input").each(function(index){$(this).css('visibility','visible');});
}

function getsem(i){
 if (i==1){ return "Spring" }
 else if(i==2){ return "Summer" }
 return "Fall"
}

function price_change_text(obj, obj2change, type){
    update_price(obj, obj.attr('key'), type, obj.val())
    obj2change.html("<option>price set at "+obj.val()+"</option>");
}

function price_change(obj, type){
    update_price(obj, obj.attr('key'), type, obj.val())
}

function price_it(obj){
    price = obj.attr('price');
    for(i=1; i < 5 && i <=price; i+=1){
        obj.append("<option>$"+i.toFixed(2)+" ("+(100-i/price*100).toFixed(0)+"% off)</option>");
    }
    for(i=5; i < 50 && i<=price; i+=5){
        obj.append("<option>$"+i.toFixed(2)+" ("+(100-i/price*100).toFixed(0)+"% off)</option>");
    }
    for(i=50; i <= 100 && i<=price; i+=10){
        obj.append("<option>$"+i.toFixed(2)+" ("+(100-i/price*100).toFixed(0)+"% off)</option>");
    }
}

function delete_comment(c,u)
{
    $.ajax({
       type: "POST",
       url: "/delete_comment",
       data: {"c":c},
       success: function(){window.location.reload()}
      });
    
}
function update_price(obj, id, type, price){
     obj.html("<option>price set at "+price+"</option>");
     $.ajax({
       type: "POST",
       url: "/add_price",
       data: "id="+id+"&type="+type+"&price="+price
      });
    price_it(obj)
}

function continue_books(){
   window.open('/sections?keys='+classes,'_self','',false)
}

function get_courses(dept){
    $.ajax({
       type: "POST",
       url: "/data",
       data: "dept="+dept,
       success: function(msg){
         data = $.parseJSON(msg);
         if(data.length < 1){
            $('#course_select').html("<option>No courses found</option>");
         }
         else{
            $('#course_select').html("<option>"+data[0]+"</option>");
            for(var i = 1; i < data.length-1; i+=2){
                $('#course_select').html($('#course_select').html() + "<option id='"+data[i]+"'>"+data[i+1]+"</option>");
            }
        }
       }
      });
}

function get_sections(course){
    $.ajax({
       type: "POST",
       url: "/data",
       data: "course="+course,
       success: function(msg){
         data = $.parseJSON(msg);
         if(data.length < 1){
            $('#course_listing').html("<option>No courses found</option>");
         }
         else{
            $('#course_listing').html(get_course_code(data[0],data[1],data[2]));
            for(var i = 3; i < data.length-4; i+=5){
                $('#course_listing').html($('#course_listing').html() + get_section_code(data[i],data[i+1],data[i+2], data[i+3],data[i+4]));
            }
        }
       }
      });
}

function get_books(course){
    $('#show_books_while_finding').html("Recommended<br /><div style='color:red'>Loading...</div>");
    $.ajax({
       type: "POST",
       url: "/data",
       data: "books="+course,
       success: function(msg){
         data = $.parseJSON(msg);
         $('#show_books_while_finding').html("Recommended");
         for(i = 0; i < data.length-6; i+=7){
                $('#show_books_while_finding').html($('#show_books_while_finding').html() + 
                // book data comes in the form
                // picture link, preview link, title, author, description, price, bookid.
                get_book_code(data[i],data[i+1],data[i+2],data[i+3],data[i+4],data[i+5],data[i+6]));
            }
        
            if(data.length > 0){
                $('#show_books_while_finding').html($('#show_books_while_finding').html() + 
                    "<a  id='poweredby' target='_blank' href='http://www.google.com'><img src='/img/poweredby.png' /></a>");
            }
        }
      });
}

function setObj(obj,ub_id,ub_price,type, book_id,book_price){
    var newobj = $("<select onchange='price_change($(this),\""+type+"\")' class='price_"+type+"' key='"+ub_id+"' price='"+book_price+"'></select>");
    obj.replaceWith(newobj);
    if(ub_price){
        newobj.append("<option>your price: "+ub_price+"</option>");
    }
    else{
        newobj.append("<option>your price: not set</option>");
    }
    price_it(newobj)
}

function user_act(obj, type, book_id){
     obj.css('color', 'gray')
     obj.attr('href', "javascript: void(0);")
     obj.html("added")
     $.ajax({
       type: "POST",
       url: "/act/",
       data: "type="+type+"&book="+book_id,
       error: function(){
            obj.css('color','red');
            obj.html('sign in!');
            obj.attr('href','');
        }
    });
}

function user_price_act(obj,type,book_id, book_price){
     obj.css('color', 'gray')
     obj.attr('href', "javascript: void(0);")
     obj.html("added")
    $.ajax({
       type: "POST",
       url: "/act/",
       data: "type="+type+"&book="+book_id,
       error: function(){
            obj.css('color','red');
            obj.html('sign in!');
            obj.attr('href','');
        },
       success: function(msg){
         data = $.parseJSON(msg);
         setObj(obj,data[0],data[1],type, book_id, book_price);
      }
    });
}

function do_course_select(){
    $('#course_select').removeAttr("disabled");
    $('#select_ok').click(function(){do_section_select()});
    dept = $('#dept_select').attr('value');
    get_courses(dept);
}

function do_section_select(){
    course = $('#course_select :selected').attr('id');
    get_sections(course);
    get_books(course);
}

function get_course_code(cdept, cnumber, cname){
 return "<div class='course_listing_class'>"+
        "<div id='course_listing_name'>"+cname+"</div>"+
        "<div id='course_listing_number'>"+cdept+" "+cnumber+"</div>"+
        "</div>";
}

function get_book_code(pic_link, prev_link, title, author, description, price, bookid,n){
 if (n!=1){
 return "<div class='book_listing' id='"+bookid+"'>"+
        "<div class='book_item_pic'>"+
        "<a target='_blank' href='/book/"+bookid+"'><img src='"+pic_link+"' /></a>"+
        "<a target='_blank' href='/book/"+bookid+"'>more info</a><br />"+
        "<a target='_blank' href='"+prev_link+"'>preview</a><br />"+
        "<a class='want_it' id='w"+bookid+"' onclick='user_act($(this),\"want\", \""+bookid+"\")' href='javascript:return false;'>want it</a><br />"+
        "<a class='have_it' id='h"+bookid+"' onclick='user_act($(this),\"have\", \""+bookid+"\")' href='javascript:return false;'>have it</a><br />"+
        "</div>"+
        "<div class='book_item_desc'>"+
            "<div class='book_title'><a target='_blank' href='/book/"+bookid+"'>"+title+"</a></div>"+
            "<div class='book_author'>"+author+"</div>"+
            "<div class='book_desc'>"+description+"</div>"+
            "<div class='book_price'>$"+price+"</div>"+
        "</div>"+
        "</div>";
    }
else{
return "<div class='big_book_listing' id='"+bookid+"'>"+
        "<div class='big_book_item_pic'>"+
        "<a target='_blank' href='/book/"+bookid+"'><img src='"+pic_link.replace("zoom=5","zoom=1")+"' /></a>"+
        "</div>"+
        "<div class='big_book_item_desc'>"+
            "<div class='big_book_title'><a target='_blank' href='/book/"+bookid+"'>"+title+"</a></div>"+
            "<div class='big_book_author'>"+author+"</div>"+
            "<div class='big_book_desc'>"+description+"</div>"+
            "<div class='big_book_price'>$"+price+"</div>"+
        "<a target='_blank' href='/book/"+bookid+"'>more info</a> | "+
        "<a target='_blank' href='"+prev_link+"'>preview</a> | "+
        "<a class='want_it' id='w"+bookid+"' onclick='user_act($(this),\"want\", \""+bookid+"\")' href='javascript:return false;'>want it</a> | "+
        "<a class='have_it' id='h"+bookid+"' onclick='user_act($(this),\"have\", \""+bookid+"\")' href='javascript:return false;'>have it</a><br />"+
        "</div>"+
        "</div>";
    }
}

function get_book_code_late(obj, classn){
$.ajax({
       type: "POST",
       url: "/getbooksforclass",
       data: "class="+classn,
       success: function(msg){
            m = $.parseJSON(msg);
            for(i=0; i < m.length; i++){
                obj.append(get_book_code(m[i][0],m[i][1],m[i][2],m[i][3],m[i][4],m[i][5],m[i][6],1));
            }
        }
      });
}











var depts = new Array(
'ACCT','ACLG','ACLS','ACTU','AFAS','AFCV','AFEN','AFRS','AHHS','AHIS','AHMM','AHUM','AKAD',
'AMCS','AMHS','AMST','ANCS','ANES','ANHS','ANTH','APAM','APBM','APMA','APPH','ARAM','ARCH',
'ASAM','ASCE','ASCM','ASPH','ASRL','ASST','ASTR','AUAH','AUAN','AUAT','AUBI','AUCA','AUCC',
'AUCE','AUCF','AUCL','AUCR','AUCS','AUCV','AUCZ','AUEC','AUEN','AUER','AUFL','AUFS','AUHA',
'AUHE','AUHS','AULS','AUMH','AUMS','AUPH','AUPS','AUPY','AURL','AURS','AUSL','AUSO','AWAY',
'BCHM','BENG','BERK','BHSC','BICO','BIET','BINF','BIOC','BIOL','BIOT','BIST','BMCH','BMEB',
'BMEN','BMME','BUEC','BUEX','BULW','BUSI','CANT','CATL','CBMF','CHAP','CHEE','CHEM','CHEN',
'CHNS','CIEE','CIEN','CLAH','CLCV','CLCZ','CLEA','CLEN','CLFR','CLGM','CLGR','CLHS','CLIA',
'CLLT','CLME','CLPH','CLPS','CLRS','CLSL','CLSP','CLSW','CMBS','CNAD','COCI','COMH','COMM',
'COMS','COPR','CORE','CORP','CPLS','CPLT','CPMD','CPRO','CREA','CSEE','CSER','CSOR','CSPH',
'CZCH','DERM','DNCE','DNSC','DRAN','DTCH','EAAS','EAEE','EAIA','EARL','EAST','ECBM','ECHS',
'ECIA','ECON','ECPH','EDUC','EEBM','EECS','EEEB','EEME','EESC','EGYP','EHSC','ELEN','EMPA',
'EMPH','ENDO','ENGI','ENGL','ENME','ENRE','ENTA','ENTH','ENVB','ENVP','EPID','EXIP','EXRS',
'EXSC','FILM','FINC','FINM','FINN','FLXM','FLXO','FLXP','FOVA','FREN','FUND','FYSB','GEND',
'GEOR','GERM','GEST','GMTH','GNPH','GRAP','GREK','GRKM','GSAS','HAUS','HIST','HKNG','HNGR',
'HOSP','HPMN','HPSC','HRMG','HRSL','HRTS','HSEA','HSME','HSPB','HSPP','HSPS','HUMA','IAEX',
'IALW','IDRM','IEME','IEOR','IMPL','INAF','INBU','INDO','INSM','INST','INTC','IRSH','ITAL',
'JAZZ','JBMP','JOUR','JPNS','JWST','KORN','KYTO','LAND','LATN','LATS','LCRS','LING','LOND',
'LWPS','MATH','MDES','MEBM','MECE','MEDI','MEDR','MGMT','MICR','MIMD','MRKT','MSAE','MTFC',
'MUSI','NBHV','NECR','NEUR','NMED','NSBV','NURS','NUTR','OBSG','OCCT','OHMA','OPDN','OPHT',
'OPMN','ORBL','ORSG','ORTH','ORTS','OTOL','PAMD','PARS','PATH','PDNT','PEDI','PEDS','PEPM',
'PHAR','PHED','PHGH','PHIL','PHMD','PHYS','PHYT','PLAN','POLI','POLS','POPF','PORT','PROS',
'PSCA','PSLG','PSYC','PSYH','PUAF','PUBH','PUNJ','QMSS','QUCH','REGI','REGN','REID','RELI',
'RESI','RMAN','RSRH','RUSS','RWJS','SCNC','SCPP','SCRB','SDEV','SIEO','SIPA','SLLN','SLLT',
'SOCI','SOCW','SOEN','SOSC','SPAN','SPPO','SPRT','STAB','STAT','STOM','SUMA','SWED','SWHL',
'TAGA','THEA','THTR','TIBT','TMGT','UKRN','URBS','UTBS','UTBX','UTCE','UTCH','UTCI','UTCS',
'UTCT','UTCW','UTEC','UTFE','UTNT','UTOT','UTPS','UTRE','UTST','UTSU','UTWR','UZBK','VIAR',
'VIET','WLOF','WMST','WRIT','YIDD','ZULU');
