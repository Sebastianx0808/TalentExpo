from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
import requests
from .models import Candidate, Director, Login_Table, Place, Post, Talents
from django.core.files.storage import FileSystemStorage
import random
import string
import smtplib
from email.message import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST
from google.cloud import dialogflow_v2 as dialogflow
from django.conf import settings
import os
import uuid

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

def HomePage(request):
    return render(request, 'home.html')

def register_candidate(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        contact_details = request.POST['contact_details']
        skills = request.POST['skills']
        brief_description = request.POST['brief_description']
        profile_pic = request.FILES['profile_pic']
        email = request.POST['email']
        password = request.POST['password']
        location = request.POST['location']
        
        with transaction.atomic():
            login_entry = Login_Table.objects.create(email=email, password=password, role='candidate')
            candidate = Candidate.objects.create(
                name=name,
                age=age,
                contact_details=contact_details,
                skills=skills,
                brief_description=brief_description,
                profile_pic=profile_pic,
                login=login_entry,
                location=location
            )
        
        return redirect('home')
    places = Place.objects.all()
    
    return render(request, 'candidate_register.html', {'places': places})

def register_director(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        contact_details = request.POST['contact_details']
        designation = request.POST['designation']
        company = request.POST['company']
        brief_description = request.POST['brief_description']
        email = request.POST['email']
        password = request.POST['password']
        profile_photo = request.FILES.get('profile_photo', None)

        with transaction.atomic():
            login_entry = Login_Table.objects.create(email=email, password=password, role='director')
            director = Director.objects.create(
                name=name,
                age=age,
                contact_details=contact_details,
                designation=designation,
                company=company,
                brief_description=brief_description,
                login=login_entry
            )
            if profile_photo:
                director.profile_photo = profile_photo
                director.save()

        return redirect('home')
    return render(request, 'Director_register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            
            user = Login_Table.objects.get(email=email)
            if user.password == password:
                
                try:
                    candidate = Candidate.objects.get(login=user)
                   
                    request.session['Uname'] = candidate.name
                    request.session['Loginid'] = user.id
                    print(user.id)
                    request.session['Role'] = 'Candidate'
                    return redirect('candidate_dashboard')  # Redirect to candidate dashboard
                except Candidate.DoesNotExist:
                    pass  # Candidate not found, continue to check Director
                
                # Check if the user is a Director
                try:
                    director = Director.objects.get(login=user)
                    # Set session variables
                    request.session['Uname'] = director.name
                    request.session['Loginid'] = user.id
                    request.session['Role'] = 'Director'
                    return redirect('director_dashboard')  # Redirect to director dashboard
                except Director.DoesNotExist:
                    pass  # Director not found, invalid login

                messages.error(request, 'Invalid email or password.')
            else:
                messages.error(request, 'Invalid email or password.')
        except Login_Table.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'Login.html')

def logout(request):
    if "Loginid" in request.session:
        del request.session["Loginid"]
        del request.session['Uname']
        del request.session['Role']
    return redirect('/login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Adminindex(request):
    logid = request.session.get('Loginid')
    logname = request.session.get('Uname')
    if logid:
        return render(request, "Admin/index.html", {'Loginid': logid, 'Logname': logname})
    else:
        return HttpResponse("<script>alert('Authentication Required Please login first');window.location='/login';</script>")
    



    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def candidate_dashboard(request):
    logname = request.session.get('Uname')
    if logname:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            posts = Post.objects.order_by('-created_at').values('id', 'description', 'media', 'created_at', 'name')
            posts_list = list(posts)
            return JsonResponse({'posts': posts_list})
        else:
            return render(request, 'CandPage.html', {'logname': logname})
    else:
        return HttpResponse("<script>alert('Authentication Required Please login first');window.location='/login';</script>")
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def director_dashboard(request):
    logname = request.session.get('Uname')
    if logname:

        places = Place.objects.all()
        return render(request, 'DirecPage.html', {'logname': logname, 'places': places})
    else:
        return HttpResponse("<script>alert('Authentication Required Please login first');window.location='/login';</script>")
    

def show_candidates(request):
    if request.method == 'GET':
        candidates = Candidate.objects.all().values('id','name', 'age', 'contact_details', 'skills', 'brief_description', 'profile_pic')
        candidates_list = list(candidates)
        for candidate in candidates_list:
            print(candidate['id'])
        return JsonResponse({'candidates' : candidates_list})
def show_posts(request):
    if request.method == 'GET':
        posts = Post.objects.order_by('-created_at').values('id', 'description', 'media', 'created_at', 'name', 'role')
        posts_list = list(posts)  # Convert QuerySet to list
        return JsonResponse({'posts': posts_list})
    
def new_post(request):
    role = "candidate" if "candidate" in request.path else None
    print(role)
    if request.method == 'POST':
        name = request.POST.get('Name')
        description = request.POST.get('description')
        talent_category_id = request.POST.get('talent_category')
        media_file = request.FILES.get('media')

        # Check if all required fields are present
        if name and description and talent_category_id and media_file:
            try:
                talent_category = Talents.objects.get(pk=talent_category_id)
                post = Post.objects.create(
                    description=description,
                    talent_category=talent_category,
                    media=media_file,
                    name=name,
                    role = role
                )
                # Successfully created post
                return redirect('candidate_dashboard')  # Redirect to the home page
            except Talents.DoesNotExist:
                # Handle if talent category does not exist
                return render(request, 'New_Post.html', {'error': 'Talent category does not exist.'})
        else:
            # Handle if any required field is missing
            return render(request, 'New_Post.html', {'error': 'Please fill in all required fields.'})
    
    # Render the new post page if request method is not POST
    talents = Talents.objects.all()  # Get all talents for the drop
    return render(request, 'New_Post.html', {'talents': talents})

def check_email(request):
    email = request.GET.get('email', None)
    is_taken = Login_Table.objects.filter(email__iexact=email).exists()
    data = {
        'is_taken': is_taken
    }
    return JsonResponse(data)

def view_candidates_and_directors(request):
    
    candidates = Candidate.objects.all()
    directors = Director.objects.all()
    
    if request.method == 'POST':
        #return HttpResponse("haii")
        director_ids = request.POST.getlist('director_ids[]')
        #return HttpResponse(director_ids)
        if director_ids:
            Director.objects.filter(id__in=director_ids).update(status=True)
            return JsonResponse({'message': 'Selected directors have been verified'})
        else:
            return JsonResponse({'error': 'No directors selected for verification'}, status=400)
        

    return render(request, 'Admin_DashBoard.html', {'candidates': candidates, 'directors': directors})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"Received email: {email}")
        try:
            user = Login_Table.objects.get(email=email)
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            print("New Password:", new_password)
            user.password = new_password
            user.save()
            print("Password Updated Successfully")

            msg = EmailMessage()
            msg.set_content(f'Hi User , Your new password to login is {new_password}')
            msg['Subject'] = "Forgot Password ?"
            msg['From'] = 'josevarghse.m@gmail.com'
            msg['To'] = email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('josevarghse.m@gmail.com', 'mnnb kgch qwlx nobu')
                smtp.send_message(msg)
                print("Send Successfully")

            return render(request, 'password_reset_done.html', {'email':email, 'message': 'A password reset link has been sent to your email.'})
        except Login_Table.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Email address not found.'})

    return render(request, 'forgot_password.html')

def add_talent(request):
    if request.method == 'POST':
        talent_name = request.POST.get('talent_name')
        if talent_name:
            Talents.objects.create(talent=talent_name)
            return JsonResponse({'message': 'Talent added successfully'})
        return JsonResponse({'error': 'Invalid Input'}, status=400)
    return JsonResponse({'error' : 'Invalid request method'}, status=400)


def add_location(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pin_code = request.POST.get('pin_code')
        if country and state and city and pin_code:
            Place.objects.create(country=country, state=state, city=city, pin_code=pin_code)
            return JsonResponse({'message': 'Location added successfully!'})
        return JsonResponse({'error': 'Invalid input!'}, status=400)
    return JsonResponse({'error': 'Invalid request method!'}, status=400)

def search_candidates(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        location = request.GET.get('location', '')

        # Filter candidates based on the search query and location
        candidates = Candidate.objects.filter(name__icontains=query)
        if location:
            candidates = candidates.filter(location__icontains=location)

        # Prepare data to send back as JSON response
        candidate_data = []
        for candidate in candidates:
            candidate_info = {
                'name': candidate.name,
                'age': candidate.age,
                'contact_details': candidate.contact_details,
                'skills': candidate.skills,
                'brief_description': candidate.brief_description,
                'profile_pic': candidate.profile_pic.url if candidate.profile_pic else ''
            }
            candidate_data.append(candidate_info)

        return JsonResponse({'candidates': candidate_data})
    
def director_post(request):
    role = "director" if "director" in request.path else None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        media_file = request.FILES.get('media')

        # Check if all required fields are present
        if name and description and media_file:
            try:
                
                post = Post.objects.create(
                    description=description,
                    media=media_file,
                    name=name,
                    role = role

                )
                
                return redirect('director_dashboard') 
            except Talents.DoesNotExist:
                
                return render(request, 'Director_Post.html', {'error': 'Talent category does not exist.'})
        else:
            
            return render(request, 'Director_Post.html', {'error': 'Please fill in all required fields.'})
    
    return render(request, 'Director_Post.html' )
def send_schedule(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidateId')
        date = request.POST.get('date')
        hour = request.POST.get('hour')
        period = request.POST.get('period')
        message = request.POST.get('message')
        print(f"Received data: candidate_id={candidate_id}, date={date}, hour={hour}, period={period}, message={message}")

        try:
            candidate = Candidate.objects.get(id=candidate_id)
            print("Candidate id")
            email = candidate.login.email
            print(f"Candidate email: {email}")

            msg = EmailMessage()
            msg.set_content(f'Hi, You have a scheduled audition on {date} at {hour}:{period}. Message: {message}')
            msg['Subject'] = "Audition Schedule"
            msg['From'] = 'josevarghse.m@gmail.com' 
            msg['To'] = email

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('josevarghse.m@gmail.com', 'mnnb kgch qwlx nobu')
                    smtp.send_message(msg)
                    print("Email sent successfully")

                return JsonResponse({'success': True, 'message': 'Email sent successfully'})
            except Exception as email_exception:
                print(f"Failed to send email: {email_exception}")
                return JsonResponse({'success': False, 'error': 'Failed to send email'})

        except Candidate.DoesNotExist:
            print("Candidate not found.")
            return JsonResponse({'success': False, 'error': 'Candidate not found'})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    print("Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_directors(request):
    directors = Director.objects.all()
    directors_data = [
        {
            "name": director.name,
            "age": director.age,
            "contact_details": director.contact_details,
            "designation": director.designation,
            "company": director.company,
            "brief_description": director.brief_description,
            "status": director.status,
        }
        for director in directors
    ]
    return JsonResponse({"directors": directors_data})


def search_directors(request):
    query = request.GET.get('query', '')
    directors = Director.objects.filter(name__icontains=query)
    serialized_directors = [{'name': director.name, 'age': director.age, 'contact_details': director.contact_details,
                             'designation': director.designation, 'company': director.company,
                             'brief_description': director.brief_description} for director in directors]
    return JsonResponse({'directors': serialized_directors})


def get_profile(request):
    login_id = request.session.get('Loginid')
    
    if login_id:
        try:
            login_instance = Login_Table.objects.get(id=login_id)
            candidate = get_object_or_404(Candidate, login=login_instance)

            profile_data = {
                'name': candidate.name,
                'age': candidate.age,
                'contact_details': candidate.contact_details,
                'skills': candidate.skills,
                'brief_description': candidate.brief_description,
                'profile_picture': candidate.profile_pic.url if candidate.profile_pic else 'default.jpg',
                'location': candidate.location
            }
            return JsonResponse({'profile': profile_data})
        
        except Login_Table.DoesNotExist:
            return JsonResponse({'error': 'Login Table entry does not exist.'}, status=404)
        except Candidate.DoesNotExist:
            return JsonResponse({'error': 'Candidate profile does not exist.'}, status=404)
    else:
        return JsonResponse({'error': 'Loginid not found in session.'}, status=400)


@csrf_exempt
def chatbot_response(request):
    user_input = request.POST.get('input')
    response = requests.post('http://localhost:5000/chat', json={'input': user_input})
    return JsonResponse(response.json())

def direc_profile(request):
    loginid = request.session.get('Loginid')
    print("The login id is: ", loginid)
    if loginid:
        try:
            login_instance = Login_Table.objects.get(id=loginid)
            director = get_object_or_404(Director, login=login_instance)

            profile_data = {
                'name': director.name,
                'age': director.age,
                'contact_details': director.contact_details,
                'designation' : director.designation,
                'company': director.company,
                'brief_description': director.brief_description,
                
            }
            return JsonResponse({'profile': profile_data})
        
        except Login_Table.DoesNotExist:
            return JsonResponse({'error': 'Login Table entry does not exist.'}, status=404)
        except Director.DoesNotExist:
            return JsonResponse({'error': ' Director profile does not exist.'}, status=404)

    
    else:
        return JsonResponse({'error': 'Loginid not found in session.'}, status=400)
    



@csrf_exempt
def delete_candidate(request):
    if request.method == 'POST':
        loginid = request.POST.get('login_id')


        if not loginid:
            return JsonResponse({'error': 'Loginid not provided.'}, status=400)
        try:
            login_instance = Login_Table.objects.get(id=loginid)
            candidate_instance = Candidate.objects.get(login=login_instance)
            candidate_instance.delete()
            login_instance.delete()
            return JsonResponse({'message': 'Candidate deleted successfully.'})
        except Login_Table.DoesNotExist:
            return JsonResponse({'error': 'Login Table entry does not exist.'}, status=404)
        except Candidate.DoesNotExist:
            return JsonResponse({'error': 'Candidate profile does not exist.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
@csrf_exempt
def delete_director(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            return JsonResponse({'error': 'Email not provided.'}, status=400)
        try:
            login_instance = Login_Table.objects.get(email=email)
            director_instance = Director.objects.get(login=login_instance)
            director_instance.delete()
            login_instance.delete()
            return JsonResponse({'message': 'Director deleted successfully.'})
        except Login_Table.DoesNotExist:
            return JsonResponse({'error': 'Login Table entry does not exist.'}, status=404)
        except Director.DoesNotExist:
            return JsonResponse({'error': 'Director profile does not exist.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid Request method.'}, status=400)

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        session_id = str(uuid.uuid4())

        client = dialogflow.SessionsClient()
        session = client.session_path('talentexpo', session_id)
        text_input = dialogflow.TextInput(text=user_message, language_code='en')
        query_input = dialogflow.QueryInput(text=text_input)
        
        response = client.detect_intent(session=session, query_input=query_input)
        fulfillment_text = response.query_result.fulfillment_text

        return JsonResponse({'response': fulfillment_text})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

