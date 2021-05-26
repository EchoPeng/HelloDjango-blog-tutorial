from django import template
from ..models import Post, Category, Tag

register = template.Library()


@register.inclusion_tag('blog/inclusions/_recent_posts.html', takes_context=True)
def show_recent_posts(context, num=5):
    return {
        "recent_post_list": Post.objects.all()[:num]
    }


@register.inclusion_tag('blog/inclusions/_archives.html', takes_context=True)
def show_archives(context):
    # Post.objects.dates方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间（已去重），
    # 且是Python的date对象，精确到月份，降序排列。接受的三个参数值表明了这些含义，
    # 一个是created_time ，即Post的创建时间，month是精度，
    # order = 'DESC'表明降序排列（即离当前越近的时间越排在前面）。
    return {
        'date_list': Post.objects.dates('created_time', 'month', order='DESC'),
    }


@register.inclusion_tag('blog/inclusions/_categories.html', takes_context=True)
def show_categories(context):
    return {
        'category_list': Category.objects.all()
    }


@register.inclusion_tag('blog/inclusions/_tags.html', takes_context=True)
def show_tags(context):
    return {
        'tag_list': Tag.objects.all()
    }