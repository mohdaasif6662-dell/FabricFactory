from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .forms import SignUpForm


def signup_view(request):

    # Already logged-in user ko dashboard par redirect karo
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():

            # User create karo, lekin pehle auto-login mat karne dena
            user = form.save(commit=False)

            # Har new user ko admin approval ka wait karna hoga
            user.is_approved = False

            user.save()

            messages.success(
                request,
                'Account created successfully. Please wait for admin approval.'
            )

            return redirect('login')

    else:

        form = SignUpForm()

    return render(
        request,
        'accounts/signup.html',
        {
            'form': form
        }
    )


def login_view(request):

    # Already authenticated user
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        # Username aur password verify karo
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Approval check
            if not user.is_approved:

                messages.error(
                    request,
                    'Your account is waiting for admin approval.'
                )

                return redirect('login')

            # Approved user login kar sakta hai
            login(request, user)

            messages.success(
                request,
                'Login successful. Welcome back!'
            )

            return redirect('dashboard')

        # Wrong username/password
        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'accounts/login.html'
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('login')