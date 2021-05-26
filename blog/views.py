from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
from .models import Post, Category, Tag
import markdown
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify

# Create your views here.


def index(request):
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={
        'post_list': post_list,
    })


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 这里给markdown解析函数传递了额外的参数extensions，
    # 它是对Markdown语法的拓展，这里使用了三个拓展，
    # 分别是extra、codehilite、toc。
    # extra本身包含很多基础拓展，
    # 而codehilite是语法高亮拓展，这为后面的实现代码高亮功能提供基础，
    # 而toc则允许自动生成目录
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        # 'markdown.extensions.fenced_code',
        # 'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ])

    # convert方法将post.body中的Markdown文本解析成HTML文本
    # 而一旦调用该方法后，实例md就会多出一个toc属性，这个属性的值就是内容的目录
    post.body = md.convert(post.body)
    # print(md.toc)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    return render(request, 'blog/detail.html', context={'post': post})


def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year, created_time__month=month)
    return render(request, 'blog/index.html', context={'post_list': post_list})


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})

def tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=tag)
    return render(request, 'blog/index.html', context={'post_list': post_list})