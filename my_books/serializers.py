from rest_framework import serializers
from .models import Books, Review
from django.contrib.auth.models import User

from rest_framework.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from datetime import date
from django.utils.html import strip_tags


class UniqueTitleValidator: # class based validators, good to be used in other places i.e. serializers

    def __call__(self, value):
        if Books.objects.filter(title=value).exists():
            raise ValidationError('Book with this title already exists')


class PastDateValidator:

    def __call__(self, value):
        if value > date.today():
            raise ValidationError('Date should be in past')
        
class CapitalizeTitle:
    
    def __call__(self, value):
        return value.title() #this is not title of book, this is a builtin string method



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email' ]
        


class ReviewsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'author', 'book', 'review']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

class BooksSerializer(serializers.ModelSerializer):
    reviews = ReviewsSerializer(many=True, read_only=True)

    # 2 runs next
    title = serializers.CharField(max_length=20, required=True, validators=[UniqueTitleValidator(), ], trim_whitespace=True)    
    author = serializers.CharField(required=True, validators=[MaxLengthValidator(10)])
    published_date = serializers.DateField(required=True, validators=[PastDateValidator()])

    #1 runs first - best place for cleaning - run serializer to db
    def to_internal_value(self, data):
        if 'title' in data:
            data['title'] = strip_tags(data['title'].strip())
        return super().to_internal_value(data)
    
    #3 field validators - specific logic to one field
    def validate_title(self, value):
        if Books.objects.filter(title=value).exists():
            raise serializers.ValidationError('Duplicate title')
        return value
    
    #1 -json through serilizer FROM DB -> CLIENT (view), but keeps user format as is, last step before view
    #   opposite direction of to_internal
    def to_representation(self, instance):
        representation = super().to_representation(instance) # *IMP*: create a copy of the output, so doesnt save to DB
        # representation['title'] = instance.title.title() # this would be instead of the Class above (CapitalizeTitle)
        representation['title'] = CapitalizeTitle()(instance.title)
        return representation
    
    class Meta:
        model = Books
        fields = ['id', 'title', 'author', 'description', 'published_date', 'is_published', 'reviews']
        