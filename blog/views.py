from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
#from .forms import EmailPostForm
from .models import Post,Comment
from .forms import CommentForm
from taggit.models import Tag
from django.db.models import Count

# Create your views here.

def post_list(request, tag_slug=None):
    object_list = Post.published.all() # retrieve every tuple of the table post
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list,3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{'page':page,'posts':posts,'tag':tag})

def post_detail(request,year,month,day,slug):
    post = get_object_or_404(Post, slug=slug,status='published',publish__year=year
                         ,publish__month=month,publish__day=day)
    # list pf active comments for this post
    comments = post.comments.filter(active = True)
    if(request.method=='POST'):
        comment_form = CommentForm(data= request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit = False)
            new_comment.post = post
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id',flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    return render(request,'blog/post/detail.html',{'post':post, 'comments':comments,
                                                   'comment_form':comment_form,'similar_posts':similar_posts})

#def post_share(request,post_id):
    # post = get_object_or_404(Post,id = post_id,status='published')
    #
    # if request.method == 'POST':
    #     form = EmailPostForm(request.POST)
    #     if form.is_valid():
    #         cd = form.cleaned_data
    # else:
    #     form = EmailPostForm();
    # return render(request,'blog/post/share.html',{'post':post,'form'=form})