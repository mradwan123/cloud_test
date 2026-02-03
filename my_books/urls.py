from django.urls import path
from .views import BooksList, book_detail, ReviewListCreateAPIView, token, review_detail

app_name = 'books'
urlpatterns = [
    path('books/', BooksList.as_view(), name='books-list'),
    path('books/<int:pk>/', book_detail, name='book-detail'),
    
    path('reviews/', ReviewListCreateAPIView.as_view(), name='reviews-list'),
    path('reviews/<int:pk>/', review_detail, name='reviews-detail'),

    #Test Token view
    path('token/', token)

]