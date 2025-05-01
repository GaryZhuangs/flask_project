from flask_project.models.post import BoardModel
from flask_project.exts import db
from flask_project.models.post import PostModel
from flask_project.models.auto import UserModel,RoleModel,Permission
import random
def init_boards():
    board_names = ["Python", "Java", "C++", "C#", "JavaScript", "Go", '爬虫', '前端']
    for index, board_name in enumerate(board_names):
        board = BoardModel(name=board_name, priority=len(board_names) - index)
        db.session.add(board)
    db.session.commit()
    print("模块初始化成功")

def init_roles():
    # 运营
    operator_role = RoleModel(name="运营", desc="负责管理帖子和评论",
                         permissions=Permission.POST | Permission.COMMENT | Permission.USER)
    # 管理员
    admin_role = RoleModel(name="管理员", desc="负责整个网站的管理",
                      permissions=Permission.POST | Permission.COMMENT | Permission.USER | Permission.STAFF)
    # 开发者（权限是最大的）
    developer_role = RoleModel(name="开发者", desc="负责网站的开发", permissions=Permission.ALL_PERMISSION)

    db.session.add_all([operator_role, admin_role, developer_role])
    db.session.commit()
    print("角色添加成功！")

def bing_roles():
    user1=UserModel.query.filter_by(email="943580899@qq.com").first()
    role1=RoleModel.query.filter_by(name="开发者").first()
    user1.role=role1
    db.session.commit()
    print("用户绑定角色成功！")



def create_test_posts():
    boards=list(BoardModel.query.all())
    board_count=len(boards)
    for x in range(99):
        title="我是标题%d"%x
        content="我是内容%d"%x
        author=UserModel.query.first()
        index=random.randint(0,board_count-1)
        board=boards[index]
        post_model=PostModel(title=title, content=content, author=author)
        db.session.add(post_model)
    db.session.commit()
    print("测试帖子添加成功")