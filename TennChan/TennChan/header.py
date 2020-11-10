from django.template import *
from . import sql
import os
from .formers import *
from .Models import *
from datetime import datetime
from django.http import *
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
#from PIL import Image
import json
from functools import wraps

from django.conf import settings
from django.contrib import messages

import requests
import hashlib
import random
import string

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_PATH = SETTINGS_PATH + "\\TennChan\\templates"
pa = "C:\\Users\\kada1004\\Documents\\Programming\\python\\programmering 2\\django\\TennChan\\TennChan\\templates\\index.html"

DEFAULT = "<html><body><center><H1>DEFAULT PAGE</H1></center></body></html>"
s = sql.MySQL("localhost", "root", "qwe123!!", "tennchan") # starts an sql connection.


class CookieHandler:
	def makeCookie(cookie, cookie_uid, cookie_type = "SEC"):
		s.post(f"INSERT INTO `tennchan`.`cookie_cache` (cookie_type, cookie_uid, cookie) VALUE ('{cookie_type}', '{cookie_uid}', '{cookie}');")
	def deleteCookie(cookie):
		s.post(f"DELETE FROM `tennchan`.`cookie_cache` WHERE cookie = '{cookie}';")
	def getCookieById(userId):
		r = s.get(f"SELECT cookie FROM tennchan.cookie_cache WHERE cookie_uid = '{userId}';")
		if len(r) <= 0:
			return "None"
		return r
	def delskey(request, key):
		try:
			del request.session[key]
		except KeyError:
			pass
		return


class Security:
	def set_cookie(response, key, value, days_expire = 7):
		if days_expire is None:
			max_age = 365 * 24 * 60 * 60  #one year
		else:
			max_age = days_expire * 24 * 60 * 60 
		expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
		response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
	def get_random_key(N = 128):
		return ''.join(random.SystemRandom().choice(string.ascii_uppercase + 
			string.digits + string.ascii_lowercase) for _ in range(N))
	def getSession(request):
		if not request.session.session_key:
			request.session.create()

		return (request.session.session_key)
	def getDate():
		now = datetime.now()
		m = str(now.month)
		if len(m) <= 1:
			m = "0" + m
		y = str(now.year)[-2:]
		return f"N{y}{m}"
	def sha512(txt): return str(hashlib.sha512( str(txt).encode('utf-8') ).hexdigest())
	def md5(txt): return str(hashlib.md5( str(txt).encode('utf-8') ).hexdigest())

	def getExpDate(madd = 1):
		now = datetime.now()
		m = str(now.month+int(madd))
		if len(m) <= 1:
			m = "0" + m
		y = str(now.year)[-2:]

		d = str(now.day)
		if len(d) <= 1:
			d = "0" + d
		return f"{y}{m}{d}"

	def getId(request):

		ip = request.META["REMOTE_ADDR"]
		session_key = Security.getSession(request)

		preSet = Security.getDate()
		HIDDEN_KEY = str(settings.HASHLIB_HIDDEN_KEY)
		keys = [3, 5, 2]
		a = 0
		# scan througt ip to get ints to use as split keys, won't except first char as int
		for char in list(str(ip)[1:]): 
			try:
				x = int(char)
			except:
				continue
			else:
				keys[a] = int(char)
				a+=1
				if a >= len(keys): break
				continue
		del a
		keys.sort()
		ip = Security.md5(ip)
		final_hkey = HIDDEN_KEY[:keys[0]]
		final_hkey += session_key + HIDDEN_KEY[keys[1]:keys[2]]
		final_hkey += ip + HIDDEN_KEY[keys[2]:] 
		final_hkey = Security.sha512(final_hkey)
		final_pkey = preSet + Security.get_random_key(6)

		if s.isEmpty(f"SELECT hidden_id FROM tennchan.security_id WHERE hidden_id = '{final_hkey}';"):
			#exp_date = Security.getExpDate()
			s.post(f"INSERT INTO security_id (public_id, hidden_id, expiration_date) VALUES ('{final_pkey}', '{final_hkey}', CURRENT_TIMESTAMP);")
			return final_pkey
		else:
			return s.get(f"SELECT public_id FROM tennchan.security_id WHERE hidden_id = '{final_hkey}';")[0][0]
	def getPublicId(private_id):
		return 1
	def getPrivateId(public_id):
		return 1


	def getIdFromIp(ip):
		HIDDEN_KEY = str(settings.HASHLIB_HIDDEN_KEY)
		KEY_SPLIT = 5
		now = datetime.now()
		key = str(hashlib.sha512( str(HIDDEN_KEY[KEY_SPLIT:] + str(ip) + HIDDEN_KEY[:KEY_SPLIT]).encode('utf-8') ).hexdigest())
		return f"N{str(now.year)[-2:]}{now.month}{str(hashlib.md5(key.encode('utf-8')).hexdigest())}"



def check_recaptcha(view_func):
	# https://simpleisbetterthancomplex.com/tutorial/2017/02/21/how-to-add-recaptcha-to-django-site.html
	# https://www.google.com/recaptcha/admin/site/433652915
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		request.recaptcha_is_valid = None
		if request.method == 'POST':
			recaptcha_response = request.POST.get('g-recaptcha-response')
			data = {
				'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
				'response': recaptcha_response
			}
			r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
			result = r.json()
			if result['success']:
				request.recaptcha_is_valid = True
			else:
				request.recaptcha_is_valid = False
				messages.error(request, 'Invalid reCAPTCHA. Please try again.')
		return view_func(request, *args, **kwargs)
	return _wrapped_view

class Captcha:
	SECRET_KEY = settings.GOOGLE_RECAPTCHA_SECRET_KEY
	SITE_KEY = settings.GOOGLE_RECAPTCHA_SITE_KEY

def err(request, txt, title="ERROR"):
	return render(request, "error.html", context={
		"error_msg": txt,
		"title": title
	})
def getDate():
	now = datetime.now()
	return f"{now.year}-{now.month}-{now.day}, {now.hour}:{now.minute}:{now.second}"
def isInt(var):
	try:
		s = int(var)
		return True
	except:
		return False
def ban(txt):
	return txt.strip().replace("'", "\\'").replace("*", "\\*").replace("<", "&lt;").replace(">", "&gt;")

def getReq(req):
	req = str(req)
	if len(req) >= 3:
		if req[:3] == "?q=":
			req = req[3:]
		else:
			req = ""
	else:
		req = ""
	postBoard = ""
	rv = []
	if len(req) >= 1:
		current = ""
		for char in req.split():
			if char == '&':
				if len(current) > 0:
					rv.append(current)
				current = ""
				continue
			current+=str(char)
		if len(current) > 0:
			rv.append(current)
	return rv