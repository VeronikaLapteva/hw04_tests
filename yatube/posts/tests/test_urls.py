from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user2 = User.objects.create_user(username='NoName2')
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_page_url_exists_at_desired_location(self):
        pages = {
            'Home': '/',
            'group_list': '/group/test_group_slug/',
            'profile': f'/profile/{PostsURLTests.user.username}/',
            'post_detail': '/posts/1/'
        }
        for page, url in pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница доступна автору поста."""
        if PostsURLTests.user == PostsURLTests.author:
            response = self.authorized_client.get('/posts/1/edit/')
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_redirect_guest(self):
        response = self.guest_client.get(
            reverse('posts:post_create'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_redirect_guest(self):
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_edit_redirect_author(self):
        response = self.authorized_client2.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            follow=True)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id}))

    def test_unexisting_page_url(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_group_slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
