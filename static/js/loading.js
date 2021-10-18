window.addEventListener("DOMContentLoaded", (event) => {
    let request = new XMLHttpRequest();
    
    request.open('POST', '/process');
    request.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    request.send(0);
    
    request.onload = function() {
        
        if (request.status === 200 && JSON.parse(request.responseText).code === 'done') {
            let requestManage = new XMLHttpRequest();
            
            requestManage.open('POST', '/manage');
            requestManage.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            requestManage.send(0);
            
            requestManage.onload = function() {
                
                if (requestManage.status === 200 && JSON.parse(requestManage.responseText).code === 'done') {
                    
                    window.location = '/manage';
                
                } else {
                   
                    alert('ERROR')
                
                }
            };
        
        } else if(request.status === 200 && JSON.parse(request.responseText).code === 'token') {
            
            window.location = '/token';
        
        } else {
            
            alert('ERROR')
        
        }
    };
});