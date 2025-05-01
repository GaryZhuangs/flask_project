var SettingHandler = function () {
}

SettingHandler.prototype.listenAvatarUploadEvent = function () {
    $("#avatar-input").on("change", function () {
        var image = this.files[0];
        if (image) {
            var formData = new FormData();
            formData.append("image", image);  // 修改字段名以匹配后端
            zlajax.post({
                url: "/avatar/upload",
                data: formData,
                contentType: false,  // 确保设置正确
                processData: false,
                success: function (result) {
                    if (result.code == 200) {
                        var avator=result['data']['avatar']
                        var avatar_url = "/media/avatar/"+avator
                        $("#avatar-img").attr("src", avatar_url);
                    }
                }
            });
        }
    });
}

SettingHandler.prototype.listenSubmitEvent = function () {
    $("#submit-btn").on("click", function (event) {
     event.preventDefault();
     var signature = $("#signature-input").val();
     var name=$("#name-input").val();
     if(!name){
         alert("请输入昵称");
         return ;
     }
     if(!signature){
         alert("提交成功")
         return ;
     }
     if(signature.length>200){
         alert("签名不能超过200个字符");
         return ;
         }
     zlajax.post({
         url: "/profile/edit",
         data:{signature:signature,
               username:name},
         success: function (result) {
             if (result['code'] == 200) {
                 alert("提交成功")
                 window.location.reload();
             }
             else{
                 alert(result.message)
             }
         }

     })
    });
}

SettingHandler.prototype.run = function () {
    this.listenAvatarUploadEvent();
    this.listenSubmitEvent();
}

$(function () {
    var handler = new SettingHandler();
    handler.run();
})