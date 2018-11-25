from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from products.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import *
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.core.mail import EmailMessage
import datetime
from datetime import timedelta

from userprofile.models import FreshUserIp


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        verify_user = User.objects.filter(username=username)
        verify_email = User.objects.filter(email=email)
        if verify_user:
            return render(request, 'signup.html', {'error': 'UserName Already Exists..'})
        elif verify_email:
            return render(request, 'signup.html', {'error': 'Email Already Exists..'})
        else:
            user = User(username=username, email=email, password=password)
            user.save()
            return redirect('/login_user/')
    else:
        return render(request, 'signup.html')


def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.filter(username__contains=username, password=password) | \
               User.objects.filter(email__contains=username, password=password)
        if user:
            for us in user:
                if us.is_active:
                    request.session['username'] = us.username
                    login(request, us)
                    return HttpResponseRedirect('/')
        else:
            msg = 'Username or Password is wrong.'
            context = {'error': msg}
            return render(request, 'login.html', context)

    return render(request, 'login.html', )


def logout_view(request):
    logout(request)
    del request.session['username']
    return redirect('home')


def update(request):
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email']
        if password != '' and email != '':
            query = User.objects.filter(
                username=request.session['username']
            ).update(password=password, email=email)
            return redirect('/')
    else:
        # defaults = {
        #             'username': request.user.username,
        #             'email': request.user.email,
        #         }
        # if request.user.profile.userAllergies:
        #     defaults['allergies'] = [t.pk for t in request.user.profile.userAllergies.all()]
        #     print (defaults)
        # form = UpDateForm(defaults, instance=request.user)
        return render(request, 'update.html', )


def update_forgot_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email']
        if password != '':
            query = User.objects.filter(email__contains=email).update(password=password)
            return JsonResponse({'status': 'pass', 'message': 'Password Update'})
    else:
        return JsonResponse({'status': 'Fail', 'message': 'Some Error Occured'})


def update_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        if password != '':
            query = User.objects.filter(username=request.session['username']).update(password=password)
            return redirect('/')
    else:
        return render(request, 'password.html', )


def forgot_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        if password != '':
            query = User.objects.filter(username=request.session['username']).update(password=password)
            return redirect('/')
    else:
        return render(request, 'forgot_password.html', )


def featured(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        check_favorite = Featured.objects.filter(username=request.session['username'], product_id=product_id)
        if check_favorite:
            return JsonResponse({'success': True, 'message': 'Product Already in Your Favorite List'})
        else:
            feature = Featured(product_id=product_id, username=request.session['username'])
            feature.save()
            return JsonResponse({'success': True, 'message': 'Product Added Successfully..'})


def favorite_products(request):
    products = []
    if request.session['username'] != '':
        favourite = []
        favorites = Featured.objects.filter(username=request.session['username'])
        for fv in favorites:
            favourite.append(int(fv.product_id))
    favroties = Featured.objects.filter(username=request.session['username'])
    for item in favroties:
        productss = Product.objects.filter(productId=item.product_id)
        for p in productss:
            products.append(p)
    context = {'products': products, 'favourites': favourite}
    return render(request, 'favorite_items.html', context)


def remove_favorite(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        remove_favorites = Featured.objects.filter(username=request.session['username'], product_id=product_id)
        remove_favorites.delete()
        return JsonResponse({'success': True, 'message': 'Product Deleted Successfully..'})


def home(request):
    from django.core.paginator import Paginator
    if request.method == 'GET':
        category = Category.objects.all()
        try:
            allergens = request.session.get('allergies_filter', '')
        except NameError:
            allergens = []
        allergies_list = []
        for allergy in allergens:
            if allergy:
                allergies_list.append(allergy.replace(',', ''))
        allergies_query = Allergy.objects.filter(allergyName__in=allergies_list)
        alergy_ids = []
        for allergies_item in allergies_query:
            alergy_ids.append(allergies_item.allergyId)
        all_products = Product.objects.exclude(productAllergies__in=alergy_ids)
        page = request.GET.get('page', 1)
        paginator = Paginator(all_products, 25)  # Show 25 contacts per page
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        if request.user.is_authenticated:
            favourite = []
            favorites = Featured.objects.filter(username=request.session['username'])
            for fv in favorites:
                favourite.append(int(fv.product_id))
            context = {'products': products,
                       'favourites': favourite
                       }
        else:
            context = {'products': products, }
        try:
            ids = request.session.get('allergies_filter_id', '')
        except NameError:
            ids = None

        context['search_value_id'] = ids
        return render(request, 'home.html', context)


def search(request):
    if request.method == 'GET':
        try:
            allergens = request.session.get('allergies_filter', '')
        except NameError:
            allergens = []
        allergies_list = []
        for val in allergens:
            if val:
                allergies_list.append(val.replace(',', ''))
        allergies_query = Allergy.objects.filter(allergyName__in=allergies_list)
        alergy_ids = []
        for allergies_item in allergies_query:
            alergy_ids.append(allergies_item.allergyId)
        if request.GET['search_option'] == 'category':
            brand = Brand.objects.filter(brandName__contains=request.GET['search_value'])
            product = Product.objects.filter(productBrand=brand).\
                exclude(productAllergies__in=alergy_ids).order_by('productName')
        if request.GET['search_option'] == 'product':
            product = Product.objects.filter(productName__contains=request.GET['search_value']).\
                exclude(productAllergies__in=alergy_ids)
        products = []
        for p in product:
            products.append(p)
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 25)  # Show 25 contacts per page
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context = {'products': products}
    return render(request, 'search.html', context)


def verify_email(request):
    if request.method == 'POST':
        email = request.POST['email']
        verify_email = User.objects.filter(email__contains=email)
        print('++++++++++++++++++++++++++++++++++++')
        print(verify_email)
        print('++++++++++++++++++++++++++++++++++++')
        if verify_email:
            import random
            num = random.randint(0, 99999)
            number = str(num)
            add_code = VerificationCode(email__contains=email, code=number, used=False)
            add_code.save()
            send_email = EmailMessage('Reset Password Code', "Here is your code for password reset "
                                                             "please enter this code in within 5 minutes"+number,
                                      to=[email, 'wdeveloper12@gmail.com'])
            send_email.send()
            return JsonResponse({'status': 'pass', 'message': 'Code Sent on Email: ' + email})
        else:
            return JsonResponse({'status': 'Fail', 'message': 'Wrong Email User does not Exist'})


def confirm_code(request):
    if request.method == 'POST':
        email = request.POST['email']
        code = request.POST['code']
        verify_code = VerificationCode.objects.filter(email=email, code=code, used=False)
        current_time = datetime.datetime.now()
        if verify_code:
            for v in verify_code:
                this_time = v.created_at + timedelta(hours=1, minutes=5)
                verify_time = this_time.time().strftime("%I:%M")
                if current_time.time().strftime("%I:%M") >= verify_time:
                    update_token = VerificationCode.objects.filter(code=code).update(used=True)
                    return JsonResponse({'status': 'Fail', 'message': 'Token Expired'})
                else:
                    update_token = VerificationCode.objects.filter(code=code).update(used=True)
                    return JsonResponse({'status': 'pass', 'message': 'Token Verified'})
        else:
            return JsonResponse({'status': 'Fail', 'message': 'Wrong Token or have already used.'})


def search_allergies(request):
    if request.method == 'GET':
        search_value = []
        search_values = request.GET['search_value'].split(',')
        for val in search_values:
            if val:
                search_value.append(val.replace(',', ''))
        request.session['allergies_filter'] = search_value
        search_value_id = []
        search_value_ids = request.GET['search_value_id'].split(',')
        for id in search_value_ids:
            if id:
                search_value_id.append(id.replace(',', ''))
        alergy = Allergy.objects.filter(allergyName__in=search_value)
        alergy_ids = []
        for alergy_id in alergy:
            alergy_ids.append(alergy_id.allergyId)
        product = Product.objects.exclude(productAllergies__in=alergy_ids)
        products = []
        for p in product:
            products.append(p)
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 25)  # Show 25 contacts per page
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        request.session['allergies_filter_id'] = search_value_id
        context = {'products': products, 'search_val': search_value, 'search_value_id': search_value_id}
        return render(request, 'home.html', context)


def verify_ip(request):
    user_data = request.POST['ip_adress'].replace('{', '').replace('}', '').split(',')
    user_data = user_data
    ip_address = user_data[0].split(':')
    ip_address = ip_address[1].replace('"', '').replace(' ', '')
    country_name = user_data[5].split(':')
    country_name = country_name[1].replace(' ', '').replace('"', '')
    users_ip = FreshUserIp.objects.filter(ip_address=ip_address)
    if not users_ip:
        user_ip = FreshUserIp(
            ip_address=ip_address,
            location=country_name
        )
        user_ip.save()
    return JsonResponse({'status': 'pass', 'message': 'IP Inserted'})


def check_ip(request):
    user_data = request.POST['ip_adress'].replace('{', '').replace('}', '').split(',')
    user_data = user_data
    ip_address = user_data[0].split(':')
    ip_address = ip_address[1].replace('"', '').replace(' ', '')
    users_ip = FreshUserIp.objects.filter(ip_address=ip_address)
    if not users_ip:
        return JsonResponse({'status': 'pass', 'message': 'Not Found'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Found'})


def terms_and_condition(request):
    return render(request, 'terms_and_conditions.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')
