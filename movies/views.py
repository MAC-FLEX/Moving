from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from .models import Movie, Rating, Cast, Genre
from .forms import RatingForm
import random

# Create your views here.
def index(request):
    recommends = []
    movies = Movie.objects.all()
    pick = random.choice(movies)
    recommends = []
    while len(recommends) < 3 :
        tmp = random.choice(movies)
        if tmp not in recommends:
            recommends.append(tmp)
    context = {'pick': pick, 'recommends': recommends}
    return render(request, 'movies/index.html', context)


def movie_list(request):
    movies = Movie.objects.all()
    genres = Genre.objects.all()
    context = {'movies': movies, 'genres': genres}
    return render(request, 'movies/movie_list.html', context)


def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = movie.rating_set.all()
    review_form = RatingForm()
    review_update_form = RatingForm()
    tmp = list(movie.cast_set.all())
    tmp.pop(0)
    casts = tmp
    cast_first = movie.cast_set.first()
    
    # # score avg
    # score_list = []
    # for review in reviews:
    #     score_list.append(review.score)
    # score_avg = sum(score_list) / len(reviews)
    context = {'movie': movie, 'reviews': reviews, 'review_form': review_form, 'casts': casts, 'cast_first':cast_first, 'review_update_form': review_update_form,}
    return render(request, 'movies/detail.html', context)


@require_POST
def review_create(request, movie_pk):
    if request.user.is_authenticated:
        review_form = RatingForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie_id = movie_pk
            review.user = request.user
            review.save()
    return redirect('movies:detail', movie_pk)


@require_POST
def review_delete(request, movie_pk, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Rating, pk=review_pk)
        if review.user == request.user:
            review.delete()
        return redirect('movies:detail', movie_pk)
    return HttpResponse('You ar Unauthorized', status=401)

@login_required
def review_update(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Rating, pk=review_pk)
    if request.user == review.user:
        if request.method == 'POST':
            review_update_form = RatingForm(request.POST, instance=review)
            if review_update_form.is_valid():
                review = review_update_form.save(commit=False)
                review.movie = movie
                review.user = request.user
                review.save()
                return redirect('movies:detail', movie_pk)
    return redirect('movies:detail', movie_pk)
    
def update(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    if request.method == 'POST':
        article.title = request.POST.get('title')#기존의 인스턴스 변수 값을 새로 할당
        article.content = request.POST.get('content')
        article.image = request.FILES.get('image')
        article.save()
        return redirect(article) #get_absolute_url을 쓰면 객체만 넣어주면 detail로..!
        # return redirect('articles:detail', article.pk)
    else:
        context = {'article': article,}
        return render(request, 'articles/update.html', context)


def like(request, movie_pk):
    if request.is_ajax():
        movie = get_object_or_404(Movie, pk=movie_pk)
        # user = request.user
        if movie.like_users.filter(pk=request.user.pk).exists():
            movie.like_users.remove(request.user)
            liked = False
        else:
            movie.like_users.add(request.user)
            liked = True
        
        context = {'liked': liked, 'count': movie.like_users.count(),}
        return JsonResponse(context)
    else:
        return HttpResponseBadRequest()