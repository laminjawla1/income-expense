from django.shortcuts import render
from .forms import ProfileUpdateForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Profile updated successfully 😊")
            return redirect('profile')
    else:
       user_form = UserUpdateForm(instance=request.user)
       profile_form = ProfileUpdateForm(instance=request.user.profile) 

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
