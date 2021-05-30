from django import template
from ..models import Post, Category, Tag
from django.db.models.aggregates import Count

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
    # Count方法接收一个和Categoty相关联的模型参数名（这里是Post，通过ForeignKey关联的），
    # 然后它便会统计Category记录的集合中每条记录下的与之关联的Post记录的行数，也就是文章数，
    # 最后把这个值保存到num_posts属性中。
    category_list = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'category_list': category_list
    }


@register.inclusion_tag('blog/inclusions/_tags.html', takes_context=True)
def show_tags(context):
    tag_list = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'tag_list': tag_list
    }