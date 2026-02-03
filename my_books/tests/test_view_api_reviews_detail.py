from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Books, Review
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


class ReviewDetailTest(TestCase):
    """Test Authentication with and without Tokens, test Methods. Create setUp."""
    
    def setUp(self):
        """
        will contain: token, book, user, owner_user, review, admin_user, client, url
        """ 
       
       #create owner of review
        self.user1 = User.objects.create(
           username='user1',
           password='user1pass',
           email='user1@email.com'
       )
       # create random user
        self.user2 = User.objects.create(
           username='user2',
           password='user2pass',
           email='user2@email.com'
       )
        
        self.admin = User.objects.create_superuser(
           username='admin',
           password='adminpass',
           email='admin@email.com'
       )
        
        #taking from model
        self.book = Books.objects.create(
            title='test book',
            author='test author',
            published_date='2020-01-01',
            description = 'test description'
        )
        
        self.review=Review.objects.create(
            author = self.user1,
            book = self.book,
            review = 'Review 1'
        )
        
        # Token setup
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.token_admin = Token.objects.create(user=self.admin)
        
        # Creating a mock client to send request to backend instead of Postman - use APIClient
        self.client = APIClient()
        
        self.url = lambda pk: reverse('books:reviews-detail', args=[pk])
        
    def test_get_review_detail_unauthenticated_client(self):
        response = self.client.get(self.url(self.review.id)) #using GET method, id already exists in db
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.id, response.data['id'])
        self.assertEqual(self.review.review, response.data['review'])    
        self.assertEqual(response.data['author']['username'], self.user1.username)
        
    def test_get_review_detail_unauthenticated_client_not_existing_review_id(self):
        response = self.client.get(self.url(999999999999999)) #checking with id that doesnt exist
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_update_review_with_review_author_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        
        updated_data = {
            'review':'PUT update review',
            'book': self.book.pk,
        }
        
        response = self.client.put(
            self.url(self.review.id),
            updated_data,
            format = 'json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, 'PUT update review')
        
    def test_put_update_review_not_author_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token2.key}") #not the user owner 

        updated_data = {
            'review':'PUT update review',
            'book': self.book.pk,
        }
        
        response = self.client.put(
            self.url(self.review.id),
            updated_data,
            format = 'json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)