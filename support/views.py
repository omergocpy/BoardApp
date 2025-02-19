from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SupportRequest, Message
from .forms import SupportRequestForm, MessageForm

@login_required
def support_request_list(request):
    requests = SupportRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support_request_list.html', {'requests': requests})

@login_required
def support_request_create(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            return redirect('support_request_list')
    else:
        form = SupportRequestForm()
    return render(request, 'support_request_form.html', {'form': form})

@login_required
def support_request_detail(request, pk):
    support_request = get_object_or_404(SupportRequest, pk=pk)
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.support_request = support_request
            message.save()
            return redirect('support_request_detail', pk=pk)
    else:
        message_form = MessageForm()

    messages = support_request.messages.all().order_by('created_at')
    return render(request, 'support_request_detail.html', {
        'support_request': support_request,
        'messages': messages,
        'message_form': message_form
    })
