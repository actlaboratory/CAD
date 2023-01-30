# -*- coding: utf-8 -*-
# request sender
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import sys
import traceback

import requests
import requests.exceptions

import constants


from logging import getLogger


log = getLogger("%s.%s" % (constants.LOG_PREFIX, "requestSender"))


class RequestSender:
	@classmethod
	def send(cls, req):
		data = {
			"RequestInfo": {
				"method": req.getMethod().name,
				"url": req.getUri,
			},
			"RequestBody":None,
		}
		req = req.toRequests()
		data["RequestInfo"]["headers"] = req.headers
		try:
			data["RequestBody"] = json.loads(req.body)
		except:
			if req.body:
				data["RequestBody"] = str(req.body)
			else:
				data["RequestBody"] = None

		with requests.Session() as sess:
			import socket
			try:
				res = sess.send(req, allow_redirects=False, timeout=10)
			except requests.exceptions.Timeout as e:
				return cls._errorResponse(data, _("タイムアウトが発生しました。"), e)
			except requests.exceptions.SSLError as e:
				return cls._errorResponse(data, _("SSL通信の開始に失敗しました。"), e)
			except requests.exceptions.ConnectionError as e:
				return cls._errorResponse(data, _("接続できませんでした。"), e)
			except requests.exceptions.TooManyRedirects as e:
				return cls._errorResponse(data, _("リダイレクトの回数が上限を超えました。"), e)
			except requests.exceptions.RequestException as e:	# 関連例外の親玉。ここには来ないでほしい。
				return cls._errorResponse(data, _("エラーが発生しました。"), e)

			data["ResponseInfo"]={}
			data["ResponseBody"]=None

			data["ResponseInfo"]["status_code"] = res.status_code
			data["ResponseInfo"]["reason"] = res.reason
			data["ResponseInfo"]["elapsed"] = res.elapsed
			data["ResponseInfo"]["headers"] = res.headers
			try:
				data["ResponseBody"] = res.json()
			except:
				data["ResponseBody"] = res.text
			return data

	@classmethod
	def _errorResponse(cls, data, msg, e):
			log.error(traceback.format_exc())
			data["error"] = msg
			data["detail"] = str(e)
			return data
