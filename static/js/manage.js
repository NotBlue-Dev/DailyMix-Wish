// MOSTLY GRAPHIC MODIFICATION

let jinja;

let select = []

function setVal(arg) {
    jinja = arg
}

window.addEventListener("DOMContentLoaded", (event) => {
    
    let formID = document.getElementById("formID");
    let x = document.createElement("INPUT");
    x.setAttribute("type", "checkbox");
    x.setAttribute("id", "genres");
    x.setAttribute("onclick", "options(this)");

    val = jinja
    if (val == 'True') {
        x.checked = true
    } else {
        x.checked = false
    }
    formID.prepend(x);

});

function deleteTracks() {
    select.forEach(item => {
        document.getElementById(item).outerHTML = "";
    });
    let counter = document.getElementById('counter')
    counter.innerText = 0
    
    let request = new XMLHttpRequest();
    
    request.open('POST', '/delete');
    request.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    val = `tab=${select}`
    request.send(val);

    select = []

}

function checkboxClicked(arg) {
    if (arg.checked) {
        select.push(arg.id)
    } else {
        select.splice(select.indexOf(arg.id),1)
    }
    
    let counter = document.getElementById('counter')
    counter.innerText = select.length
}

function options(element) {
    let request = new XMLHttpRequest();
    request.open('POST', '/options');
    request.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    if(element.checked) {
        request.send("genre=0");
    } else {
        request.send("genre=1");
    }
}

function newMix() {
    let load = document.getElementById("load");
    let all = document.getElementById("all");

    load.style.display = 'block'
    all.style.display = 'none'

    let request = new XMLHttpRequest();

    request.open('POST', '/newMix');
    request.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    request.send(0);
    
    request.onload = function() {
        
        if (request.status === 200 && request.responseText === 'success') {
            
            load.style.display = 'none'
            all.style.display = 'block'
            window.location = '/manage'

        } else {
            
            alert('ERROR')
        }
    
    };
}

function switchWindow(arg) {

    let user = document.getElementById("DailyUser");
    let daily = document.getElementById("DailyCont");
    let opt = document.getElementById("optionsDiv");
    let big = document.getElementById("big");
    let all = document.getElementById("all");
    let trash = document.getElementById("trash");

    all.style.display = 'block';
    big.style.display = 'block';
    opt.style.display = 'none';
    daily.style.display = 'none';
    user.style.display = 'none';
    trash.style.display = 'block';

    let tracks = document.getElementById("trackss");
    let dailys = document.getElementById("dailys");
    let opts = document.getElementById("optionss");

    opts.classList.remove('active');
    dailys.classList.remove('active');
    tracks.classList.remove("active");

    let counter = document.getElementById('counter')
    counter.innerText = 0
    select = []

    switch (arg) {
        
        case "user":
            user.style.display = 'block'
            tracks.classList.add('active')
            trash.style.display = 'none';
            break;
    
        case "daily":
            daily.style.display = 'block'
            dailys.classList.add('active')
            break;

        case "options":
            big.style.display = 'none'
            opt.style.display = 'block'
            opts.classList.add('active')
            break;
    }
}