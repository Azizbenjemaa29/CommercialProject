from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def opportunites(request):
    url = request.GET.get('url', '')
    return render(request, 'opportunites.html', {'target_url': url})


