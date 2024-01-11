import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from matplotlib.pyplot import xlabel
from numpy import require
from yahoo_fin.stock_info import *
import queue
import requests
from threading import Thread
from django.forms import inlineformset_factory
from django.contrib import messages
from .forms import CreateUserForm,UserUpdateForm, profileUpdateForm
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from .models import UserAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from celery.schedules import crontab
#from celery.task import periodic_task
from django.views.decorators.csrf import csrf_exempt
import pandas as pd	
import newspaper
from django.contrib import messages
from .forms import CreateUserForm
from .models import news, UserAccount
import razorpay

from django.contrib.auth.forms import PasswordChangeForm

#contact forms
from .forms import ContactForm
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


import random

import pandas as pd
from pandas import DataFrame
import plotly.express as px

from yahoo_fin import stock_info

#top gainers and loosers
from nsetools import Nse

import urllib.request

# Create your views here.
def home(request):
	host='http://google.com'
	try:
		urllib.request.urlopen(host)
		if request.method == 'GET':
			form = ContactForm()
		else:
			form = ContactForm(request.POST)
			if form.is_valid():
				name = form.cleaned_data['name']
				email = form.cleaned_data['email']
				phone = form.cleaned_data['phone']
				message = form.cleaned_data['message']
				try:
					send_mail("From Email:- "+email, "Phone Number:- "+phone+" "+message, email , [settings.EMAIL_HOST_USER], fail_silently=False)
				except BadHeaderError:
					return HttpResponse("Error")
				return redirect('Base:home')

		# fetching the top gainers and loosers		
		nse = Nse()
		gainers = nse.get_top_gainers()
		print("Gainers:- ",gainers)
		loosers = nse.get_top_losers()
		print(loosers)
		
		return render(request,'home.html', {'form': form,'gainers':gainers,'loosers':loosers})
		
	except:
		return HttpResponse("<script>window.alert('Please Check Your Internet Connection')</script>")
	

	

def register(request):
    return render(request,'register.html')

@login_required
def userProfile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = profileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			print('success')
			messages.success(request=request, message="Profile Updated!!!")

		else:
			u_form.errors.update(p_form.errors)
			print(u_form.errors)
			messages.error(request=request, message=u_form.errors)
		return redirect('Base:userprofile')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = profileUpdateForm(instance=request.user.profile)
		context = {
			#'username':u_form['username'].value(),
			'email':u_form['email'].value(),
			'u_form': u_form,
			'p_form': p_form,
		}
		return render(request,template_name='userprofile.html', context=context)

@login_required
def changePassword(request):
	if request.method == 'POST':
		fm= PasswordChangeForm(user=request.user, data=request.POST)
		if fm.is_valid():
			fm.save()
			update_session_auth_hash(request,fm.user)
			return HttpResponseRedirect('/userprofile/')
		else:
			print("form error**************")
			messages.error(request=request, message="Error")
			
	
	fm=PasswordChangeForm(user=request.user)
	u_form = UserUpdateForm(instance=request.user)
	context = {
		#'username':u_form['username'].value(),
		'email':u_form['email'].value(),
		"form": fm
	}
		# print(fm)
	return render(request,'changepass.html',context=context)


def stockpicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)
    return render(request,'stockpicker.html',{"stockpicker":stock_picker})

async def stocktracker(request):
    stockpicker = request.GET.getlist('stockpicker')

    graphdata = request.GET['graphstockpicker']
    
    print(stockpicker)
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")

    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()

    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}), args = (que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)


    print(data)
    return render(request,'stocktracker.html',{"data":data,'room_name':'track','graph_stock':graphdata})




def loginPage(request):
	if request.user.is_authenticated:
		return redirect('Base:home')
	else:
		if request.method == "POST":
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username,password=password)
			

			if user is not None:
				request.session['username'] = user.get_username()
				print(request.session['username'])
				#request.session['loggeduser'] = username
				try:
					data = UserAccount.objects.get(user=user)
				except:
					data = None

				if data is None:
					print("Not a Pro User")
					login(request, user)
					request.session['loggeduser'] = False
					return redirect("Base:otp")
				else:
					print("A pro user")
					request.session['loggeduser'] = True
					login(request, user)
					return redirect("Base:otp")       
			else:
				print("User is none*************")
				messages.error(request=request,message='Username or Password is Incorrect')
				
		return render(request, 'login.html')

	

global generated_otp
generated_otp = 0

@login_required
def otp(request):
	global generated_otp
	if request.method == "POST":
		otp = request.POST.get('otp')
		if int(otp) == int(generated_otp):
			# request.session['loggedin'] = True
			return redirect("Base:home") 
		else:
			messages.error(request,'OTP verification failed.!')
			logout(request)
			generated_otp=0
			return render(request,"login.html")
	else:
		generated_otp = random.randrange(1000,9999)
		print(generated_otp)
		u = User.objects.get(username = request.session['username'])
		user_email = u.email
		send_mail("Tradexa OTP Verification","Please enter the OTP to login:- "+str(generated_otp), settings.EMAIL_HOST_USER, [user_email],fail_silently=False)
		return render(request,"otp.html")

@login_required
def logoutUser(request):
	logout(request)
	return redirect('Base:home')


def registerPage(request):
	form = CreateUserForm()
	
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			# user = form.cleaned_data.get('username')
			messages.success(request,'Account created successfully')

			return redirect('Base:login')

	context={'form': form}
	return render(request, 'register.html', context)

def tips(request):
	return render(request, 'tips.html')

def handler404(request):
    return redirect("404.html")

def handler500(request):
    return redirect("500.html")

# def get_news():

# 	newspaper_links = [ 'https://www.cnbctv18.com/market/',	'https://finance.yahoo.com/topic/stock-market-news/']

# 	unwanted_links = ['https://finance.yahoo.com/u/yahoo-finance/watchlists/tech-stocks-that-move-the-market',
# 	'https://finance.yahoo.com/u/yahoo-finance/watchlists/stocks-with-the-highest-short-interest',
# 	'https://finance.yahoo.com/u/yahoo-finance/watchlists/most-sold-by-activist-hedge-funds',
# 	'https://finance.yahoo.com/u/yahoo-finance/watchlists/most-bought-by-activist-hedge-funds',
# 	'https://finance.yahoo.com/tech/video',
# 	'https://finance.yahoo.com/calendar/economic',
# 	'https://finance.yahoo.com/calendar/splits',
# 	'https://finance.yahoo.com/calendar/earnings'
# 	'https://finance.yahoo.com/calendar/ipo'
# 	]

# 	df_articles = pd.DataFrame(columns=['headline', 'link', 'img'])

# 	for link in newspaper_links:
# 		paper = newspaper.build(link, memoize_articles=False)

# 		print(len(paper.articles))
# 		# i = 0
# 		# stop = 40
# 		for i in range(0, len(paper.articles)):
# 			if i < len(paper.articles):
# 				if link == 'https://finance.yahoo.com/topic/stock-market-news/':
# 					if 'finance' in paper.articles[i].url:
# 						print(link)
# 						art = newspaper.Article(paper.articles[i].url)
# 						art.download()
# 						art.parse()
# 						# article_meta_data = article.meta_data
# 						# published_date = {value for (key, value) in article_meta_data.items() if key == 'date.created'}
# 						# article_published_date = " ".join(str(x) for x in published_date)
# 						# date =  art.publish_date #datetime.strptime(str(art.publish_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
# 							# date = datetime.strptime(str(article.publish_date), '%Y-%m-%d %H:%M:%S'
# 						artlink = art.url	
# 						img = art.top_image
# 						headline = art.title

# 						if '?' in artlink:
# 							temp = artlink.split('?')[0]
# 							if temp not in unwanted_links:
# 								print(artlink)
# 								df_articles = df_articles.append({'headline': headline, 'link': artlink, 'img_url': img}, ignore_index=True)	
# 						elif artlink not in unwanted_links:
# 							df_articles = df_articles.append({'headline': headline, 'link': artlink, 'img_url': img}, ignore_index=True)
# 				else:
# 					art = newspaper.Article(paper.articles[i].url)
# 					art.download()
# 					art.parse()
# 					# article_meta_data = article.meta_data
# 					# published_date = {value for (key, value) in article_meta_data.items() if key == 'date.created'}
# 					# article_published_date = " ".join(str(x) for x in published_date)
# 					# date =  art.publish_date #datetime.strptime(str(art.publish_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
# 						# date = datetime.strptime(str(article.publish_date), '%Y-%m-%d %H:%M:%S'
# 					artlink = art.url	
# 					img = art.top_image
# 					headline = art.title
# 					df_articles = df_articles.append({'headline': headline, 'link': artlink, 'img_url': img}, ignore_index=True)

# 				# i += 1
# 			# print(len(df_articles))

# 	# df_dict = df_articles.to_dict('records')
# 	for index, row in df_articles.iterrows():
# 		print(f'saving.. {index}')
# 		# try:
# 		# if index < 10:
# 		n = news()
# 		n.headlines = row['headline']
# 		n.link = row['link']
# 		n.img_url = row['img_url']
# 		n.save()
		# except :
			# print(e)


	# URL = 'https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2l3bk55c0JCRXQ0RnZ1WWQ3ZTFTZ0FQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen&so=1'
	# page = requests.get(URL)
	# soup = BeautifulSoup(page.content, 'html.parser')
	# # prefix = 'news.google.com'
	# df_articles = pd.DataFrame(columns=['Headlines', 'link'])
	# # all_articles = soup.find_all('article')
	# prefix = 'https://news.google.com'
	# # df_articles = pd.DataFrame(columns=['Headlines', 'link'])
	# # linkss_all = {}
	
	# for art in soup.find_all('h3'):
		
	# 	a = art.find('a')
	# 	if a.has_attr('href'):
	# 		headline = art.text
	# #         print(type(headline))
	# 		link = prefix + a['href'][1:]
	# #         print(type(link))
	# 		# build_news = build_article(url=link)
	# 		# break
	# 		df_articles = df_articles.append({'Headlines': headline, 'link': link}, ignore_index=True)

	# df_dict = df_articles.to_dict('records')
	# # for index, row in df_articles.iterrows():
	# # 	print(row['Headlines'], row['link'])
	# for index, row in df_articles.iterrows():
	# 	# try:
	# 	if index < 10:
	# 		n = news()
	# 		n.headlines = row['Headlines']
	# 		n.link = row['link']
	# 		n.save()
	# 	else:
	# 		break
		# except:
	
	# for art in df_dict:
	# 	print(art['Headlines'])
	# 	break
	# print(df_dict)

	# return df_dict


def stock_news(request):
	# get_news()

	url = ('https://newsapi.org/v2/everything?q=stock%20market&apiKey=ac23c00b91904a218237b957a5f3e519')

	response = requests.get(url)
	dump_dict = response.json()
	print(dump_dict)
	print('='*100)
	news_articles = pd.DataFrame(columns=['url', 'img_url', 'headline', 'description', 'author'])

	for dump in dump_dict['articles']:
		author = dump['author']
		headline = dump['title']
		description = dump['description']
		art_url = dump['url']
		img_url = dump['urlToImage']

		# print(f"'url': {art_url}, 'author': {author}, 'headline': {headline}, 'description': {description}, 'img_url':{img_url}")

		news_articles = pd.concat([news_articles,pd.DataFrame({'url': [art_url], 'author': [author], 'headline': [headline], 'description': [description], 'img_url':[img_url]})],ignore_index=True)
		# break


	print('='*100)
	print('\n')
	print(news_articles.to_dict('index'))
	news_articles = news_articles.to_dict('index')

	# news_articles = news.objects.order_by('-date')
	context ={'articles': news_articles}
	# context ={'articles': hola}
	# print(context)

	return render(request=request, template_name='blogs.html', context=context)
	
def proUser(request):
	if request.method == "POST":
		# print('*'*100)
		# print(request.user)
		name = request.POST.get('name')
		amount = 10000
		client = razorpay.Client(
            auth=("rzp_test_oQsuE6quyQWrpT", "SbLiQPIUnpIuQWr8yB2NgyTh"))
		payment = client.order.create({'amount': amount, 'currency': 'INR','payment_capture': '1'})
		print('*'*100)
		# temp_user = UserAccount.objects.filter(user=request.user).first()
		# if temp_user is None:
		temp_user = UserAccount(user=request.user, pro_Account = True)
		temp_user.save()	
		# print(temp_user.pro_account)
		# temp_user.pro_account = True
		# temp_user.save()

		return render(request,'success.html')
	return render(request, 'payment.html')

@csrf_exempt
def success(request):
    return render(request,'success.html')



def stockpredictionpicker(request):
	stockPicker = tickers_nifty50()
	print("Prediction picker data")
	print(stockPicker)
	return render(request,'predictionstockpicker.html',{"stockpicker":stockPicker})

def stockprediction(request):
	stock = request.GET['stockpicker']
	stockdata = get_quote_table(stock,tickers_nifty50())
	print("Stock picked:- ",stock)
	df = pd.read_csv(f'C:/Final Year Project/Final/TradeXa - Copy/assets/Predictions/{stock}.csv')
	fig = px.line(df,x="Days",y="predictions",title=f'{stock} Prediction for the next few days')
	graph = fig.to_html()
	return render(request,'stockprediction.html',{"graph":graph,"data":stockdata})


def pennystockpicker(request):
	return render(request,'pennystock.html')

def pennystockprediction(request):
	stock = request.GET["pennystockpicker"]
	df = pd.read_csv(f'C:/Final Year Project/Final/TradeXa - Copy/assets/Predictions/{stock}.csv')
	fig = px.line(df,x="Days",y="predictions",title=f'{stock} Prediction for the next few days')
	graph = fig.to_html()
	return render(request,'pennystockprediction.html',{"graph":graph})
    
