from django.db import models

class Author(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    home_page = models.URLField(blank=True,null=True)

    class Meta:
        db_table = 'authors'

class Comments(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='replies')
    text = models.TextField()
    file = models.FileField(upload_to='uploads/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

