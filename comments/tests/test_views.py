# from django.apps import apps
# from django.contrib.auth.models import User
from django.urls import reverse

# from blog.models import Category, Post

from ..models import Comment
from .base import CommentDataTestCase


class CommentViewTestCase(CommentDataTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("comments:comment", kwargs={"post_pk": self.post.pk})

    def test_comment_a_nonexistent_post(self):
        url = reverse("comments:comment", kwargs={"post_pk": 100})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)

    def test_invalid_comment_data(self):
        invalid_data = {
            "email": "invalid_email",
        }
        response = self.client.post(self.url, invalid_data)
        self.assertTemplateUsed(response, "comments/preview.html")
        self.assertIn("post", response.context)
        self.assertIn("form", response.context)
        form = response.context["form"]
        for field_name, errors in form.errors.items():
            for err in errors:
                self.assertContains(response, err)
        self.assertContains(response, "评论发表失败！请修改表单中的错误后重新提交。")

    def test_valid_comment_data(self):
        valid_data = {
            "name": "评论者",
            "email": "a@a.com",
            "text": "评论内容",
        }

        # 由于评论成功后需要重定向，因此传入follow = True，表示跟踪重定向，
        # 因此返回的响应，是最终重定向之后返回的响应（即被评论文章的详情页），如果传入
        # False，则不会追踪重定向，返回的响应就是一个响应码为302的重定向前响应。
        response = self.client.post(self.url, valid_data, follow=True)

        # 对于重定向响应，使用assertRedirects进行断言，
        # 这个断言方法会对重定向的整个响应的过程进行检测，默认检测的是响应码从302变为200。
        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertContains(response, "评论发表成功！")
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.name, valid_data["name"])
        self.assertEqual(comment.text, valid_data["text"])
