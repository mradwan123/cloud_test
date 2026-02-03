from django.shortcuts import render
from rest_framework.views import APIView
from .models import Books, Review
from .serializers import BooksSerializer, ReviewsSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissons import CanUpdateReview, IsAdminOrReviewAuthor

# Create your views here.

class BooksList(APIView):
    
    def get(self, request):
        books = Books.objects.all()
        serializer = BooksSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BooksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

@api_view(['GET','PUT','DELETE', 'PATCH'])
def book_detail(request, pk):
    try:
        book = Books.objects.get(pk=pk)
    except Books.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer  = BooksSerializer(book)
        return Response(serializer.data, status=200)
    
    elif request.method == 'PUT':
        serializer = BooksSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'PATCH':
        serializer = BooksSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        book.delete()
        return Response(status=204)
    
    
################ Reviews Class

class ReviewListCreateAPIView(APIView):
    
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    
    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewsSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ReviewsSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.http import HttpResponse

def token(request):
    user = User.objects.get(username='test2')
    token = Token.objects.create(user=user)
    return HttpResponse(token)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication, ])
def review_detail(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response(status=404)
    

    if request.method == 'GET':
        serializer = ReviewsSerializer(review)
        return Response(serializer.data, status=200)
    
    elif request.method in ['PUT', 'PATCH']:
        permission = CanUpdateReview()
        if not permission.has_object_permission(request=request, obj=review):
            return Response({"error": "You dont have permission"}, status=403)
        
        partial = request.method == 'PATCH'
        serializer = ReviewsSerializer(
            review, 
            data=request.data, 
            context={'request': request}, 
            partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, 400)
    
    elif request.method == 'DELETE':
        permission = IsAdminOrReviewAuthor()
        if not permission.has_object_permission(request=request, obj=review):
            return Response({"error": "You dont have permission"}, status=403)
        
        review.delete()
        return Response(status=204)