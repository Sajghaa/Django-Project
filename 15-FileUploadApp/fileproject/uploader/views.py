from django.shortcuts import render, redirect, get_object_or_404
from .models import UploadedFile
from .forms import FileUploadForm

def file_list(request):
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    return render(request, 'uploader/file_list.html', {'files': files})

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'uploader/upload_form.html', {'form': form})

def file_detail(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    return render(request, 'uploader/file_detail.html', {'file': file})

def delete_file(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    if request.method == 'POST':
        file.delete()
        return redirect('file_list')
    return render(request, 'uploader/confirm_delete.html', {'file': file})