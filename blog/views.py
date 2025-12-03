from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post


def redirect_with_query_param(request, key, value):
    """
    Returns a redirect response with all existing query parameters preserved,
    but with `key` replaced with `value`.
    """

    params = request.GET.copy()
    params[key] = value
    url = f"{request.path}?{params.urlencode()}"
    return redirect(url)


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"

    def get(self, request, *args, **kwargs):
        """
        Manually paginate exactly like the FBV did, so we can
        catch invalid page numbers and redirect to a corrected URL.
        """
        post_list = self.get_queryset()
        paginator = Paginator(post_list, self.paginate_by)
        page_number = request.GET.get("page", 1)

        try:
            posts_page = paginator.page(page_number)
        except PageNotAnInteger:
            return redirect_with_query_param(request, "page", 1)
        except EmptyPage:
            return redirect_with_query_param(request, "page", paginator.num_pages)

        
        context = {
            "posts": posts_page,
            "page_obj": posts_page,
            "paginator": paginator,
            "is_paginated": posts_page.has_other_pages(),
            "object_list": posts_page.object_list,
        }

        return render(request, self.template_name, context)


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        return redirect_with_query_param(request, "page", 1)
    except EmptyPage:
        return redirect_with_query_param(request, "page", paginator.num_pages)

    return render(request, "blog/post/list.html", context={"posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    return render(request, "blog/post/detail.html", context={"post": post})
