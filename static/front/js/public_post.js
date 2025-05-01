var PublicPostHandler = function() {
     var csrf_token = $('meta[name="csrf-token"]').attr('content');
     var editor = new window.wangEditor('#editor');
     editor.config.uploadImgServer = '/post/image/upload';
     editor.config.uploadFileName = 'image';
     editor.config.uploadImgHeaders = { 'X-CSRF-Token': csrf_token };
     editor.config.uploadImageMaxSize = 10 * 1024 * 1024; // 10M
     editor.create()
    this.editor=editor
}

PublicPostHandler.prototype.listenSubmitEvent=function (){
    const that=this
    $("#submit-btn").on("click",function (event){
        event.preventDefault();
        var title=$("input[name='title']").val();
        var board_id=$("select[name='board_id']").val()
        var content=that.editor.txt.html()
        zlajax.post({
            url:"/post/public",
            data:{
                title:title,
                board_id:board_id,
                content:content
            },
            success:function (result){
                if(result["code"]==200){
                    let data=result["data"];
                    let post_id=data["id"];
                    window.location='/post/detail/'+post_id;
                }
                else{
                    alert(result["message"]);
                }
            }
        })
    })
}

PublicPostHandler.prototype.run = function() {
    this.listenSubmitEvent()
}


$(function (){
    var handler=new PublicPostHandler();
    handler.run();
})