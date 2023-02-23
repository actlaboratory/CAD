# -*- coding: utf-8 -*-
# リクエストエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy
import json
import requests
import urllib.parse

import CmdLineUtil

from enumClasses import BodyFieldType, ContentType, HeaderFieldType, Method
from .BodyField import BodyField
from .Header import Header
from .BaseUri import BaseUri
from .Endpoint import Endpoint

from urllib3.util.url import parse_url


URI_MIN_LENGTH = 10

class Request:
	def __init__(self, name, contentType, method, uri, headers=[], body=[], memo=""):
		if (validateName(name) or
			type(contentType) != ContentType or
			type(method) != Method or
			validateUri(uri) or
			validateHeaders(headers) or
			validateBody(contentType, body) or
			validateMemo(memo)):
			raise ValueError()

		self.body = copy.deepcopy(body)
		self.contentType = contentType
		self.headers = copy.deepcopy(headers)
		self.memo = memo.strip()
		self.method = method
		self.name = name.strip()
		self.uri = uri


	def getBody(self):
		return copy.deepcopy(self.body)

	def getContentType(self):
		return self.contentType

	def getHeaders(self):
		return copy.deepcopy(self.headers)

	def getMemo(self):
		return self.memo

	def getMethod(self):
		return self.method

	def getName(self):
		return self.name

	def getUri(self):
		return self.uri

	def toBodyDict(self):
		data = {}
		for i in self.body:
			data[i.getName()] = i.getValue()
		return data

	def toBodyString(self):
		if self.contentType == ContentType.JSON:
			data = {}
			for i in self.body:
				data[i.getName()] = i.getValue()
			return json.dumps(data)
		elif self.contentType == ContentType.FORM:
			result = ""
			for i in self.body:
				if result:
					result += "&"
				if i.getFieldType() == BodyFieldType.ENCORDED:
					result += i.getName() + "=" + i.getValue()
				else:
					result += urllib.parse.quote(i.getName()) + "=" + urllib.parse.quote(i.getValue())
			return result
		else:
			raise NotImplementedError

	def toCurlCommand(self):
		result = ["curl"]

		for k,v in self.toHeaderDict().items():
			result.append("-H")
			if i.getFieldType() == HeaderFieldType.REMOVE:
				result.append(k+":")
			elif v:	# 中身のあるv
				result.append(k+": "+v)
			else:
				result.append(k+";")

		result.append("-X")
		result.append(self.method.name)

		if self.body:
			result.append("-d")
			result.append(self.toBodyString())

		result.append(self.uri)

		return CmdLineUtil.list2Windowscmdline(result)

	def toHeaderDict(self):
		headerDict = {}
		for i in self.headers:
			if i.getFieldType() != HeaderFieldType.REMOVE:
				headerDict[i.getName()] = i.getValue()

		# case-insencitiveで比較して、Content-Typeがなければ追加
		if self.body and "content-type" not in [v.getName().lower() for v in self.headers]:
			headerDict["Content-Type"] = self.contentType.header_value
		return headerDict

	def toRequests(self):
		req = requests.PreparedRequest()
		req.prepare(self.method.name, self.uri, self.toHeaderDict(), data=self.toBodyString())

		print(req.headers)
		for i in self.headers:
			if i.getFieldType() == HeaderFieldType.REMOVE:
				print(i.getName())
				if i.getName() in req.headers:
					del req.headers[i.getName()]
		print(req.headers)
		return req

	# --remote-nameオプション指定時に使用
	def getRemoteName(self):
		raise NotImplementedError	# TODO

	# リスト表示用項目
	def GetListTuple(self):
		return self.name, self.memo

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError

def validateBody(contentType, body):
	if contentType in (contentType.JSON, contentType.FORM):
		assert type(body) == list
		for item in body:
			assert type(item) == BodyField
	else:
		raise NotImplementedError
	return ""


def validateHeaders(headers):
	assert type(headers) == list
	for item in headers:
		assert type(item) == Header

def validateMemo(memo):
	assert isinstance(memo, str)
	return ""

def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください。")
	return ""

def validateUri(uri):
	assert isinstance(uri, str)
	uri = uri.strip()
	if len(uri) < URI_MIN_LENGTH:
		return _("URIを%d文字以上で入力してください" % URI_MIN_LENGTH)
	if not uri.startswith("https://") and not uri.startswith("http://"):
		return _("URIはhttps://またはhttp://で始まる必要があります。")
	try:
		url = parse_url(uri)
		if url.auth:
			return _("認証情報はアドレスではなくAuthorizationヘッダで指定してください。")
		elif not url.host:
			return _("アドレスにホスト名が含まれていません。")
		elif url.host.startswith(".") or url.host.startswith("*"):
			return _("ホスト名が不正です。")
	except:
		import traceback
		traceback.print_exc()
		return _("アドレスが不正です。")
	return ""

	return ""
