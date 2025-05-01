var loginHandler = function() {};

loginHandler.prototype.lisenSubmitEvent= function() {
    $('#submit-btn').on('click', function(event) {
        event.preventDefault();
        var Email = $("input[name='email']").val();
        var Password = $("input[name='password']").val();
        var remember =$("input[name='remember']").prop('checked');
        zlajax.post({
            url: '/login',
            data: {
                email: Email,
                password: Password,
                remember: remember?1:0
            },
            success: function(result) {
                    if (result["code"] == 200) {
                        var token = result["data"]["token"];
                        var user=result["data"]['user']
                        localStorage.setItem("USER_KEY", JSON.stringify(user));
                        localStorage.setItem("JWT_TOKEN_KEY", token);
                        window.location = '/';
                    }
                    else {
                        alert(result["message"]);
                    }
            }
        })
    })
}





loginHandler.prototype.run = function() {
    this.lisenSubmitEvent();
};
// 用于确保在 DOM 完全加载和解析后执行代码
$(function (){
    var handler = new loginHandler();
    handler.run();
})