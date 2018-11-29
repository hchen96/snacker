/* Search snack given index's form */
function searchSnacks(query) {
    let snack_brand = query.index_search_brand.value;
    let snack_name = query.index_search_name.value;
    let available_at_locations = query.index_search_location.value;
    window.location.href = "find_snacks/snack_name=" + snack_name + "+snack_brand=" + snack_brand +
        "+available_at_locations=" + available_at_locations;
}

function indexRegister(form) {
    let email = form.email.value;
    window.location.href = "register?email=" + email
}

/*Login the user*/
function authenticate(form) {
    $.getJSON( "https://ipapi.co/json/", function( data ) {})
        .always( function( data ) {
            $.ajax({
                type: "POST",
                url: "/login",
                data: {
                    "email": form.login_email.value,
                    "password": form.login_password.value,
                    "last_country": (data ? data.country_name : ""),
                },
                dataType: "json",
                success: function (result) {
                    window.location.href = "index";
                },
                error: function (result) {
                    alert('invalid username or password');
                }
            });
        });
}

function changePassword(form) {
    console.log(form);
    $.ajax({
        type: "POST",
        url: "/change_password",
        data: {
            "password": form.edit_password.value
        },
        dataType: "json",
        success: function (result) {
            console.log(result);
            window.location.href = "account";
        },
        error: function (result) {
            alert('invalid password');
            window.location.href = "account";
        }
    });
}

function changeUserDetails(form) {
    console.log(form);
    company = "";
    try {
        if(document.getElementById("edit_company")) {
        company = form.edit_company.value;
        }
    } catch (e) {
    }
    $.ajax({
        type: "POST",
        url: "/change_user_details",
        data: {
            "email": form.edit_email.value,
            "company_name": company,
            "first_name": form.edit_first.value,
            "last_name": form.edit_last.value,
        },
        dataType: "json",
        success: function (result) {
            console.log(result);
            window.location.href = "account";
        },
        error: function (result) {
            alert('invalid data');
        }
    });
}



/*Login the user*/
function register_user(form) {
    $.getJSON( "https://ipapi.co/json/", function( data ) {})
        .always( function( data ) {
            $.ajax({
                type: "POST",
                url: "/register",
                data: {
                    "email": form.register_email.value,
                    "password": form.register_password.value,
                    "company_name": form.register_company.value,
                    "first_name": form.register_first.value,
                    "last_name": form.register_last.value,
                    "last_country": (data ? data.country_name : ""),
                },
                dataType: "json",
                success: function (result) {
                    window.location.href = "index";
                },
                error: function (result) {
                    alert('Something wrong ' + result);
                }
            });
        });
}

function createSnack(form, selected_snack_brand) {
    // A snack submission should always create a snack regardless of the ip API status
    var location = form.available_at_location.value;
    $.getJSON( "https://ipapi.co/json/", function( data ) {})
        .always( function( data ) {
            let form = document.getElementById('create-snack-form');
            let formData = new FormData(form);
            formData.set("available_at_locations", (location != "Nothing Selected" ? location
                                                : data ? data.country_name
                                                : null));
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    var response = JSON.parse(xhr.responseText);
                    if (xhr.status === 200) {
                        window.location.href="/snack_reviews/"+ response
                    } else {
                        console.log('failed');
                    }
                }
            }

            xhr.open('POST', "/create-snack/selected_brand=" + selected_snack_brand, true);
            xhr.send(formData);
        });
}

function createReview(form, snack_id) {
    // A review submission should always create a review regardless of the ip API status
    $.getJSON( "https://ipapi.co/json/", function() {})
        .always( function( data ) {
            $.ajax({
                type: "POST",
                url: "/create-review/snack_id=" + snack_id,
                data: {
                    "description": form.description.value,
                    "review_country": (data ? data.country_name : null),
                    "overall_rating": form.overall_rating.value,
                    "sourness": form.sourness.value,
                    "spiciness": form.spiciness.value,
                    "saltiness": form.saltiness.value,
                    "bitterness": form.bitterness.value,
                    "sweetness": form.sweetness.value,
                },
                success: function (result) {
                    window.location.href="/snack_reviews/snack_id="+snack_id
                },
                error: function (result) {
                    alert('Something wrong ' + result);
                }
            });
        });
}

function verify_snack(snack_id) {
    console.log(snack_id);
    $.ajax({
        type: "POST",
        url: "/verify-snack",
        data: {
            "snack_id": snack_id
        },
        dataType: "json",
        success: function (result) {
            alert("Snack verified!");
            window.location.href="/snack_reviews/snack_id="+snack_id;
        },
        error: function (result) {
            alert('Something wrong ' + result);
        }
    });
}


function change_to_fav(snack_id) {
    console.log(snack_id);
    $.ajax({
        type: "POST",
        url: "/change_to_fav",
        data: {
            "snack_id": snack_id,
        },
        dataType: "json",
        success: function (result) {
            if (String(result) == "subscribed") {
                document.getElementById(snack_id).title = "Unsubscribe from wishlist";
                document.getElementById(snack_id).getElementsByTagName("i")[0].style.color = "#f85959";
                document.getElementById(snack_id).getElementsByTagName("i")[0].style.textShadow = "0px 0px 4px #f85959";
            } else {
                document.getElementById(snack_id).title = "Subscribe to wishlist";
                document.getElementById(snack_id).getElementsByTagName("i")[0].style.textShadow = null;
                document.getElementById(snack_id).getElementsByTagName("i")[0].style.color = "#FFFFFF";
            }
        },
        error: function (result) {
            alert("Error");
        }
    });
}


function change_to_fav_wishlist(snack_id) {
    console.log(snack_id);
    $.ajax({
        type: "POST",
        url: "/change_to_fav",
        data: {
            "snack_id": snack_id,
        },
        dataType: "json",
        success: function (result) {
            if (String(result) == "subscribed") {
                alert("something wrong, this item shouldn't be in wishlist");
            } else {
                let node = document.getElementById(snack_id);
                node.parentNode.removeChild(node);
            }
        },
        error: function (result) {
            alert("Error");
        }
    });
}

// Adapted W3schools autocomplete

var currentFocus;

/*execute a function when someone writes in the text field:*/
function autocompleteListener(inp, arr) {
    var a, b, i, val = inp.value;
    /*close any already open lists of autocompleted values*/
    closeAllLists(inp);
    if (!val) { return false;}
    currentFocus = -1;
    max_show = 5;
    count = 0;
    /*create a DIV element that will contain the items (values):*/
    a = document.createElement("DIV");
    a.setAttribute("id", inp.id + "_autocomplete-list");
    a.setAttribute("class", "autocomplete-items");

    /*append the DIV element as a child of the autocomplete container:*/
    inp.parentNode.appendChild(a);
    /*for each item in the array...*/
    for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");

            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
                inp.focus();
            });
            a.appendChild(b);
            count += 1;
        }
        if (count >= max_show) {break;}
    }
}

function closeAllLists(inp, elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
            x[i].parentNode.removeChild(x[i]);
        }
    }
}

function autocompleteKeydown(e, inp) {
    var x = document.getElementById(inp.id + "_autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
    } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
    } else if (e.keyCode == 13) {
        if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) {
                x[currentFocus].click();
            }
        }
    }
}

function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
}

function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
  }
}

function toString(objectID) {
    return objectID.toString();
}