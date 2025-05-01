$(function (){
  // 初始化代码高亮
  hljs.highlightAll();

  $("#comment-btn").on("click", function (event){
    event.preventDefault();
    var $this = $(this);

    var user_id = $this.attr("data-user-id");
    if(!user_id || user_id == ""){
      window.location = "/login";
      return;
    }

    var content = $("#comment-textarea").val();
    var post_id = $this.attr("data-post-id");

    zlajax.post({
      url: "/comment",
      data: {content, post_id},
      success: function (result){
        if(result['code'] == 200){
          window.location.reload();
        }else{
          alert(result['message']);
        }
      }
    })
  });
  // 收藏
  $("#collect-btn").on("click", function (event){
    event.preventDefault();
    var $this = $(this);
    var btn_text=$this.text();
    var post_id = $this.attr("data-post-id");
    if(btn_text=="收藏"){
    zlajax.post({
      url: "/post/collect",
      data: {post_id},
      success: function (result){
        if(result['code'] == 200){
          $this.addClass("active");
          alert("收藏成功");
          window.location.reload();
        }else{
          alert(result['message']);
        }
      }
    })}
    else if(btn_text=="取消收藏"){
      zlajax.post({
        url: "/post/uncollect",
        data: {post_id},
        success: function (result){
          if(result['code'] == 200){
            $this.removeClass("active");
            alert("取消收藏成功");
            window.location.reload();
          }else
          {
            alert(result['message']);
          }
        }
      })
    }
  })
});