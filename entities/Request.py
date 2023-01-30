# -*- coding: utf-8 -*-
# リクエストエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy
import json
import requests

from enumClasses import ContentType, HeaderFieldType, Method
from .BodyField import BodyField
from .Header import Header
from .BaseUri import BaseUri
from .Endpoint import Endpoint

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

	def toRequests(self):
		headers = copy.deepcopy(self.headers)
		data = None
		if self.contentType == ContentType.JSON:
			# case-insencitiveで比較して、Content-Typeがなければ追加
			if "content-type" not in [v.getName().lower() for v in headers]:
				headers.append(Header("Content-Type", HeaderFieldType.CONST, "application/json; charset=utf-8"))
			if self.body:
				data = {}
				for i in self.body:
					data[i.getName()] = i.getValue()
				data = json.dumps(data)
			else:
				data=None
		elif self.contentType == ContentType.FORM:
			data = None
			# case-insencitiveで比較して、Content-Typeがなければ追加
			if "content-type" not in [v.getName().lower() for v in headers]:
				headers.append(Header("Content-Type", HeaderFieldType.CONST, "application/x-www-form-urlencoded"))
			if self.body:
				data = {}
				for i in self.body:
					data[i.getName()] = i.getValue()
		else:
			raise notImplementedError

		headerDict = {}
		for i in headers:
			headerDict[i.getName()] = i.getValue()

		req = requests.PreparedRequest()
		req.prepare(self.method.name, self.uri, headerDict, data=data)
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
	return ""
