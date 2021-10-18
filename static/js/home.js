let jinja;

function redirect() {
    window.location = '/process'
}

function login() {
    if (jinja == "True") {
        window.location = '/logout'
    } else {
        // not logged
        window.location = '/token'
    }
}
window.addEventListener("DOMContentLoaded", (event) => {
    check()
})

function check() {
    if (jinja == "True") {
        document.getElementById('login').innerHTML = "Logout"
    } else {
        document.getElementById('login').innerHTML = "Login"
    }
}

function setVal(arg) {
    jinja = arg
}