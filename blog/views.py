from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse
from .models import Post, Category, Tag
import markdown
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from pure_pagination import PaginationMixin
from django.contrib import messages
from django.db.models import Q
from rest_framework.decorators import api_view
from .serializers import PostListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework import mixins

# Create your views here.


class IndexView(PaginationMixin, ListView):
    # 将model指定为Post，告诉django我要获取的模型是Post
    model = Post
    # 指定这个视图渲染的模板
    template_name = 'blog/index.html'
    # 指定获取的模型列表数据保存的变量名，这个变量会被传递给模板
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10

# def index(request):
#     post_list = Post.objects.all()
#     return render(request, 'blog/index.html', context={
#         'post_list': post_list,
#     })

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        respone = super().get(request, *args, **kwargs)

        # 将文章阅读量 + 1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()
        # 视图必须返回一个 HttpResponse 对象
        return respone
    #
    # def get_object(self, queryset=None):
    #     # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
    #     post = super().get_object(queryset=None)
    #     md = markdown.Markdown(extensions=[
    #             'markdown.extensions.extra',
    #             'markdown.extensions.codehilite',
    #             # 'markdown.extensions.fenced_code',
    #             # 'markdown.extensions.toc',
    #             TocExtension(slugify=slugify),
    #         ])
    #     post.body = md.convert(post.body)
    #     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    #     post.toc = m.group(1) if m is not None else ''
    #     return post


# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#
#     # 阅读量 +1
#     post.increase_views()
#     # 这里给markdown解析函数传递了额外的参数extensions，
#     # 它是对Markdown语法的拓展，这里使用了三个拓展，
#     # 分别是extra、codehilite、toc。
#     # extra本身包含很多基础拓展，
#     # 而codehilite是语法高亮拓展，这为后面的实现代码高亮功能提供基础，
#     # 而toc则允许自动生成目录
#     md = markdown.Markdown(extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         # 'markdown.extensions.fenced_code',
#         # 'markdown.extensions.toc',
#         TocExtension(slugify=slugify),
#     ])
#
#     # convert方法将post.body中的Markdown文本解析成HTML文本
#     # 而一旦调用该方法后，实例md就会多出一个toc属性，这个属性的值就是内容的目录
#     post.body = md.convert(post.body)
#     # print(md.toc)
#     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#     post.toc = m.group(1) if m is not None else ''
#     return render(request, 'blog/detail.html', context={'post': post})

class ArchiveView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super().get_queryset().filter(created_time__year=year, created_time__month=month)


# def archive(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year, created_time__month=month)
#     return render(request, 'blog/index.html', context={'post_list': post_list})



class CategoryView(IndexView):
    # CategoryView继承ListView时，属性和IndexView中一样，未来进一步节省代码
    # 直接继承IndexView类
    """# 将model指定为Post，告诉django我要获取的模型是Post
    model = Post
    # 指定这个视图渲染的模板
    template_name = 'blog/index.html'
    # 指定获取的模型列表数据保存的变量名，这个变量会被传递给模板
    context_object_name = 'post_list'"""

    # get_queryset方方法默认获取指定模型的全部列表数据。
    # 为了获取指定分类下的文章列表数据，我们覆写该方法，改变它的默认行为
    def get_queryset(self):
        # 在类视图中，从URL捕获的路径参数值保存在实例的kwargs属性（是一个字典）里，
        # 非路径参数值保存在实例的args属性（是一个列表）里
        # 所以使用self.kwargs.get('pk')来获取从URL捕获的分类id值。
        # 然后调用父类的get_queryset方法获得全部文章列表，紧接着就对返回的结果调用了
        # filter方法来筛选该分类下的全部文章并返回。
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super().get_queryset().filter(category=cate)

# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super().get_queryset().filter(tags=tag)


# def tag(request, pk):
#     tag = get_object_or_404(Tag, pk=pk)
#     post_list = Post.objects.filter(tags=tag)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


def search(request):
    q = request.GET.get('q')
    if not q:
        error_msg = "请输入搜索关键字"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    # Q对象用于包装查询表达式，其作用是为了提供复杂的查询逻辑。例如这里
    # Q(title__icontains=q) | Q(body__icontains=q)表示标题（title）含有关键词
    # q或者正文（body）含有关键词q ，或逻辑使用 | 符号。如果不用Q对象，就只能写成
    # title__icontains = q, body__icontains = q，这就变成标题（title）含有关键词q
    # 且正文（body）含有关键词q
    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {"post_list": post_list})

#
# # 给 api_view 装饰器传入 http_method_names 参数指定允许访问该 API 视图的 HTTP 方法
# @api_view(http_method_names=["GET"])
# def index(request):
#     post_list = Post.objects.all()
#     # 构造序列化器时可以传入单个对象，序列化器会将其序列化为一个字典；
#     # 也可以传入包含多个对象的可迭代类型（这里的post_list是一个django的QuerySet），
#     # 此时需要设置many参数为True序列化器会依次序列化每一项，返回一个列表。
#     serialize = PostListSerializer(post_list, many=True)
#     return Response(serialize.data, status=status.HTTP_200_OK)


# class IndexPostListAPIView(ListAPIView):
#     # 使用PostListSerializer序列化器（通过serializer_class指定）
#     serializer_class = PostListSerializer
#     # 序列化博客文章（Post）列表（通过queryset指定）
#     queryset = Post.objects.all()
#     # 对资源列表分页（通过pagination_class指定，PageNumberPagination会自动对资源进行分页）；
#     pagination_class = PageNumberPagination
#     # 允许任何人访问该资源（通过permission_classes指定，
#     # AllowAny权限类不对任何访问做拦截，
#     # 即允许任何人调用这个API以访问其资源）
#     permission_classes = [AllowAny,]


class PostViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny,]