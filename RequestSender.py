# -*- coding: utf-8 -*-
# request sender
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import datetime
import requests
import requests.exceptions
import traceback

import constants
import globalVars

from entities import Header, Request, Response, Traffic
from enumClasses import HeaderFieldType
from logging import getLogger


log = getLogger("%s.%s" % (constants.LOG_PREFIX, "requestSender"))


class RequestSender:
	@classmethod
	def send(cls, request):
		req = request.toRequests()

		with requests.Session() as sess:
			requested_at = datetime.datetime.now()
			try:
				res = sess.send(req, allow_redirects=False, timeout=10)
			except requests.exceptions.Timeout as e:
				return cls._errorResponse(_("タイムアウトが発生しました。"), request, requested_at, e)
			except requests.exceptions.SSLError as e:
				return cls._errorResponse(_("SSL通信の開始に失敗しました。"), request, requested_at, e)
			except requests.exceptions.ConnectionError as e:
				return cls._errorResponse(_("接続できませんでした。"), request, requested_at, e)
			except requests.exceptions.TooManyRedirects as e:
				return cls._errorResponse(_("リダイレクトの回数が上限を超えました。"), request, requested_at, e)
			except requests.exceptions.RequestException as e:	# 関連例外の親玉。ここには来ないでほしい。
				return cls._errorResponse(_("エラーが発生しました。"), request, requested_at, e)

			headers = []
			for k,v in res.headers.items():
				headers.append(Header.Header(k, HeaderFieldType.CONST, v))

			try:
				response = Response.Response(res.status_code, res.elapsed, headers, res.json(), res.reason)
			except Exception as e:
				response = Response.Response(res.status_code, res.elapsed, headers, res.text, res.reason)

			traffic = Traffic.Traffic(request, response, requested_at)
			globalVars.history.add(traffic)
			return traffic.toTreeData()

	@classmethod
	def _errorResponse(cls, msg, request, requested_at, e):
		log.error(traceback.format_exc())
		response = Response.Response(None, None, [], str(e), msg)
		traffic = Traffic.Traffic(request, response, requested_at)
		globalVars.history.add(traffic)
		return traffic.toTreeData()
