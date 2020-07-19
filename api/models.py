from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    last_request_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<User id: {}; username: {}>".format(self.id,
                                                    self.username)


class Like(models.Model):
    date = models.DateTimeField(auto_now=True)
    post_id = models.ForeignKey('Post',
                                on_delete=models.CASCADE)
    user_id = models.ForeignKey('User',
                                on_delete=models.CASCADE)

    def __str__(self):
        return "<Like id: {}; post id: {}; user id: {}>".format(self.id,
                                                                self.post_id,
                                                                self.user_id)


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()

    creation_data = models.DateTimeField(auto_now=True)
    last_update_data = models.DateTimeField(auto_now_add=True)

    user_id = models.ForeignKey('User',
                                null=True,
                                on_delete=models.SET_NULL)

    def __str__(self):
        return "<Post id: {}; title: {}>".format(self.id,
                                                 self.title)
