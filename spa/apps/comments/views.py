from django.http import JsonResponse
from django.views import View
from .models import Comments, Author
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import re
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import bleach
import cloudinary.uploader

@method_decorator(csrf_exempt, name='dispatch')
class CommentListView(View):
    def get(self, request):
        sort_by = request.GET.get('sort', 'created_at')
        order = request.GET.get('order', 'desc')
        page = int(request.GET.get('page', 1))

        allowed_sort = ['username', 'email', 'created_at']
        if sort_by not in allowed_sort:
            sort_by = 'created_at'

        if sort_by == 'username':
            order_field = 'author__username'
        elif sort_by == 'email':
            order_field = 'author__email'
        else:
            order_field = 'created_at'

        if order == 'asc':
            comments = Comments.objects.filter(parent=None).order_by(order_field)
        else:
            comments = Comments.objects.filter(parent=None).order_by(f'-{order_field}')

        per_page = 25
        start = (page - 1) * per_page
        end = start + per_page
        total = comments.count()

        def serialize_comment(c):
            return {
                'id': c.id,
                'text': c.text,
                'author': c.author.username,
                'email': c.author.email,
                'home_page': c.author.home_page or '',
                'created_at': c.created_at.isoformat(),
                'file': c.file_url,
                'replies': [serialize_comment(r) for r in c.replies.all()]
            }

        data = [serialize_comment(c) for c in comments[start:end]]
        return JsonResponse({'comments': data, 'total': total, 'page': page, 'pages': (total + per_page - 1) // per_page})

    def post(self, request):
        captcha_key = request.POST.get('captcha_key')
        captcha_value = request.POST.get('captcha_value')

        if not captcha_key or not captcha_value:
            return JsonResponse({'error': 'captcha required'}, status=400)

        try:
            store = CaptchaStore.objects.get(hashkey=captcha_key)
            if store.response != captcha_value.lower():
                return JsonResponse({'error': 'captcha invalid'}, status=400)
            store.delete()
        except CaptchaStore.DoesNotExist:
            return JsonResponse({'error': 'captcha expired'}, status=400)

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        text = request.POST.get('text', '').strip()
        home_page = request.POST.get('home_page', '')
        parent_id = request.POST.get('parent_id')

        if not username or not email or not text:
            return JsonResponse({'error': 'all field be required'}, status=400)
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return JsonResponse({'error': 'username invalid'}, status=400)
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return JsonResponse({'error': 'email invalid'}, status=400)

        text = bleach.clean(text, tags=['a', 'code', 'i', 'strong'], attributes={'a': ['href', 'title']})

        file = request.FILES.get('file')
        file_url = None

        if file:
            ext = file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'gif', 'png']:
                from PIL import Image
                from io import BytesIO
                img = Image.open(file)
                img.thumbnail((320, 240))
                buffer = BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                buffer.seek(0)
                result = cloudinary.uploader.upload(buffer, folder='uploads')
                file_url = result['secure_url']
            elif ext == 'txt':
                if file.size > 100 * 1024:
                    return JsonResponse({'error': 'txt file more 100 kb'}, status=400)
                result = cloudinary.uploader.upload(file, resource_type='raw', folder='uploads')
                file_url = result['secure_url']
            else:
                return JsonResponse({'error': 'Only JPG, GIF, PNG, TXT'}, status=400)

        author = Author.objects.create(username=username, email=email, home_page=home_page)
        comment = Comments.objects.create(author=author, text=text, parent_id=parent_id, file_url=file_url)

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'comments',
                {
                    'type': 'new_comment',
                    'comment': {
                        'id': comment.id,
                        'text': comment.text,
                        'author': comment.author.username,
                        'created_at': comment.created_at.isoformat(),
                        'file': comment.file_url,
                    }
                }
            )
        except Exception:
            pass

        return JsonResponse({
            'id': comment.id,
            'text': comment.text,
            'author': comment.author.username,
            'created_at': comment.created_at.isoformat(),
            'file': comment.file_url
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class CommentDetailView(View):
    def get(self, request, pk):
        try:
            comment = Comments.objects.get(id=pk)
        except Comments.DoesNotExist:
            return JsonResponse({"error": 'Not Found'}, status=404)

        def serialize(c):
            return {
                'id': c.id,
                'text': c.text,
                'author': c.author.username,
                'email': c.author.email,
                'created_at': c.created_at.isoformat(),
                'file': c.file_url,
                'replies': [serialize(r) for r in c.replies.all()]
            }
        return JsonResponse(serialize(comment))


@method_decorator(csrf_exempt, name='dispatch')
class CaptchaView(View):
    def get(self, request):
        captcha = CaptchaStore.generate_key()
        return JsonResponse({
            'key': captcha,
            'image': request.build_absolute_uri(captcha_image_url(captcha))
        })