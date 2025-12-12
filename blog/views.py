from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post
from .forms import EmailPostForm


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
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )
