import os
import pathlib
import random
import sys
from datetime import timedelta
import django
import faker
from django.utils import timezone

# 将项目根目录添加到 Python 的模块搜索路径中
dirname = os.path.dirname
BASE_DIR = dirname(dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == '__main__':

    # 首先设置DJANGO_SETTINGS_MODULE环境变量，这将指定django启动时使用的配置文件，
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')

    # 运行django.setup()启动django。这是关键步骤，只有在django
    # 启动后，我们才能使用django的ORM系统。django启动后，就可以导入各个模型，以便创建数据。
    django.setup()

    from blog.models import Category, Post, Tag
    from comments.models import Comment
    from django.contrib.auth.models import User

    # 这一段脚本用于清除旧数据，因此每次运行脚本，都会清除原有数据，然后重新生成。
    print('clean database')
    Post.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()
    User.objects.all().delete()

    # 简单地使用django的ORMAPI生成博客用户、分类、标签以及一篇Markdown测试文章。
    print('create a blog user')
    user = User.objects.create_superuser('echo', 'echo@github.com', 'echo')
    category_list = ['Python学习笔记', '开源项目', '工具资源', '程序员生活感悟', 'test category']
    tag_list = ['django', 'Python', 'Pipenv', 'Docker', 'Nginx', 'Elasticsearch', 'Gunicorn', 'Supervisor', 'test tag']
    a_year_ago = timezone.now() - timedelta(days=356)

    print('create categories and tags')
    for cate in category_list:
        Category.objects.create(name=cate)

    for tag in tag_list:
        Tag.objects.create(name=tag)

    print('create a markdown sample post')
    Post.objects.create(
        title='Markdown 与代码高亮测试',
        body=pathlib.Path(BASE_DIR).joinpath('scripts', 'md.sample').read_text(encoding='utf-8'),
        category=Category.objects.create(name='Markdown测试'),
        author=user,
    )

    print('create some faked posts published within the past year')
    fake = faker.Faker('zh_CN')     # 生成中文数据，为空时默认为英文
    for _ in range(100):

        # order_by('?')将返回随机排序的结果，脚本中这块代码的作用是达到随机选择标签(Tag)和分类(Category)的效果。
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()

        # 这个方法将返回2个指定日期间的随机日期。三个参数分别是起始日期，终止日期和时区。
        # 在这里设置起始日期为1年前（-1y），终止日期为当下（now），时区为get_current_timezone返回的时区
        # 时区为get_current_timezone返回的时区函数是django.utils.timezone模块的辅助函数，它会根据django设置文件中TIME_ZONE的值返回对应的时区对象
        created_time = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            # sentence随机生成字符串，根据语言类型可生成汉字
            title=fake.sentence().rstrip('.'),
            # fake.paragraphs(10)用于生成10个段落文本，以列表形式返回，列表的每个元素即为一个段落。
            # 要注意使用2个换行符连起来是为了符合arkdown语法，Markdown中只有2个换行符分隔的文本才会被解析为段落。
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()

    print('create some comments')
    for post in Post.objects.all()[:20]:
        post_created_time = post.created_time
        # 评论的发布时间必须位于被评论文章的发布时间和当前时间之间，这就是delta_in_days = '-' + str((timezone.now() - post_created_time).days) + 'd'这句代码的作用。
        # 得出发布时间和当前时间的天数差
        delta_in_days = '-' + str((timezone.now()-post_created_time).days) + 'd'
        for _ in range(random.randrange(3, 15)):
            Comment.objects.create(
                name = fake.name(),
                email= fake.email(),
                url = fake.url(),
                text = fake.paragraph(),
                created_time=fake.date_time_between(start_date=delta_in_days, end_date='now', tzinfo=timezone.get_current_timezone()),
                post=post,
            )
    print('done')