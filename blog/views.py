from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Post
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag


def redirect_with_query_param(request, key, value):
    """
    Returns a redirect response with all existing query parameters preserved,
    but with `key` replaced with `value`.
    """

    params = request.GET.copy()
    params[key] = value
    url = f"{request.path}?{params.urlencode()}"
    return redirect(url)


def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, per_page=3)
    page_number = request.GET.get("page", 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if not an integer, get the first page
        return redirect_with_query_param(request, "page", 1)
    except EmptyPage:
        # if page not found > num_pages, get the last one
        return redirect_with_query_param(request, "page", paginator.num_pages)

    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/post/list.html"

#     def get(self, request, tag_slug=None, *args, **kwargs):
#         """
#         Manually paginate exactly like the FBV did, so we can
#         catch invalid page numbers and redirect to a corrected URL.
#         """
#         tag = None
#         post_list = self.get_queryset()

#         if tag_slug:
#             tag = get_object_or_404(Tag, slug=tag_slug)
#             post_list = post_list.filter(tags__in=[tag])

#         paginator = Paginator(post_list, self.paginate_by)
#         page_number = request.GET.get("page", 1)

#         try:
#             posts_page = paginator.page(page_number)
#         except PageNotAnInteger:
#             return redirect_with_query_param(request, "page", 1)
#         except EmptyPage:
#             return redirect_with_query_param(request, "page", paginator.num_pages)

#         context = {
#             "posts": posts_page,
#             "tag": tag,
#             "page_obj": posts_page,
#             "paginator": paginator,
#             "is_paginated": posts_page.has_other_pages(),
#             "object_list": posts_page.object_list,
#         }

#         return render(request, self.template_name, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # similar posts - based on count(common tags)
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(pk=post.pk)

    similar_posts = similar_posts.annotate(common_tags_cnt=Count("tags")).order_by(
        "-common_tags_cnt", "-publish"
    )[:4]

    return render(
        request,
        "blog/post/detail.html",
        context={
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = f"{cd['name']} {cd['email']} recommends you to read {post.title}"

            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {
            "post": post,
            "form": form,
            "sent": sent,
        },
    )


# only allow POST requests
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():
        # create a comment object without saving to db
        comment = form.save(commit=False)
        # then assign the corresponding post FK to it
        comment.post = post
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )
