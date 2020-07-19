import json
import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest

from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework import status

from .serializers import (UserSignInSerializer,
                          PostSerializer,
                          LikeSerializer)
from .models import (User,
                     Post,
                     Like)


# ====================== USER VIEWS ======================


class UserSignUpAPIView(CreateAPIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        user = request.data

        serializer = UserSignInSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': 'True',
                         'status code': status.HTTP_201_CREATED,
                         'message': 'User is successfully registered'},
                        status=status.HTTP_201_CREATED)


class UserActivityAPIView(RetrieveAPIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        user = get_object_or_404(User, pk=user_id)
        return Response({'username': user.username,
                         'last login time': user.last_login,
                         'last request time': user.last_request_time})


# ====================== POSTS VIEWS ======================


class PostCreateView(CreateAPIView):
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        title = request.data['title']
        body = request.data['body']
        user = request.user

        Post.objects.create(title=title,
                            body=body,
                            user_id=user)
        return Response({'status': '200',
                         'message': 'Post is created'})


class PostListView(ListAPIView):

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        username = request.GET.get('username')
        if username is None:
            return HttpResponseBadRequest()

        user = get_object_or_404(User, username=username)
        if user is None:
            return Response({'status': status.HTTP_404_NOT_FOUND,
                             'message': "User with '{}' username does not exist".format(username)})

        posts_queryset = Post.objects.filter(user_id=user)
        serializer = PostSerializer(posts_queryset,
                                    many=True)
        return Response(serializer.data)


class PostDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['post_id']).first()
        if not post:
            return Response({'status': status.HTTP_404_NOT_FOUND,
                             'message': 'Post is not found'})
        if request.user == post.user_id:
            post.update(**request.data)
            return Response({'status': status.HTTP_200_OK,
                             'message': "Post successfully updated"})
        else:
            return Response({'status': status.HTTP_403_FORBIDDEN,
                             'message': 'Cannot update post by current user'})

    def patch(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['post_id'])
        if not post:
            return Response({'status': status.HTTP_404_NOT_FOUND,
                             'message': 'Post is not found'})
        if request.user == post.first().user_id:
            post.update(**request.data)
            return Response({'status': status.HTTP_200_OK,
                             'message': "Post successfully updated"})
        else:
            return Response({'status': status.HTTP_403_FORBIDDEN,
                             'message': 'Cannot update post by current user'})

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if request.user == post.user_id:
            post.delete()
            return Response({'status': status.HTTP_200_OK,
                             'message': "Post successfully deleted"})
        else:
            return Response({'status': status.HTTP_403_FORBIDDEN,
                             'message': 'Cannot delete post by current user'})


# ====================== LIKES VIEWS ======================


class LikePostView(DestroyAPIView,
                   CreateAPIView):

    def post(self, request, *args, **kwargs):
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        like = Like.objects.filter(post_id=post,
                                   user_id=user).first()
        if not like:
            Like.objects.create(post_id=post,
                                user_id=user)
            return Response({'status': status.HTTP_200_OK,
                             'message': 'Liked the post'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': status.HTTP_208_ALREADY_REPORTED,
                             'message': 'You have already liked the post'},
                            status=status.HTTP_208_ALREADY_REPORTED)

    def delete(self, request, *args, **kwargs):
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        like = Like.objects.filter(post_id=post,
                                   user_id=user).first()
        if like:
            like.delete()
            return Response({'status': status.HTTP_200_OK,
                             'message': 'Unliked the post'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': status.HTTP_208_ALREADY_REPORTED,
                             'message': 'You have already unliked the post'},
                            status=status.HTTP_208_ALREADY_REPORTED)


# ====================== ANALYTICS VIEWS ======================


class AnalyticsView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        user = request.user
        date_from = (int(i) for i in request.GET['date_from'].split('-'))
        date_to = (int(i) for i in request.GET['date_to'].split('-'))

        datetime_from = datetime.datetime(*date_from)
        datetime_to = datetime.datetime(*date_to,
                                        hour=23,
                                        minute=59,
                                        second=59)
        result_dict = {}

        datetime_temp = datetime_from
        one_day = datetime.timedelta(days=1)
        while datetime_temp < datetime_to:
            likes = Like.objects.filter(date__range=(datetime_temp,
                                                     datetime_temp + one_day),
                                        user_id=user)
            serializer = LikeSerializer(likes, many=True)
            result_dict[str(datetime_temp) + ' - ' + str(datetime_temp + one_day)] = len(serializer.data)
            datetime_temp += one_day

        return Response({'status': status.HTTP_200_OK,
                         'data': json.dumps(result_dict)},
                        status=status.HTTP_200_OK)
