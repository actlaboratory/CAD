# -*- coding: utf-8 -*-
# エンドポイントエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy

from enumClasses import ContentType, Method
from .BodyField import BodyField
from .Header import Header

class Endpoint:

	def __init__(self, parent, name, method, uri, body, contentType=None, headers=[], memo=""):
		if (
			validateName(name) or
			type(method) is not Method or
			validateUri(uri) or
			validateBody((contentType if contentType else parent.getContentType()), body) or
			type(contentType) is not ContentType and contentType is not None or
			validateHeaders(headers) or
			validateMemo(memo)):
			raise ValueError()
		self.aditionalHeaders = copy.deepcopy(headers)
		self.body = copy.deepcopy(body)
		self.contentType = contentType
		self.memo = memo.strip()
		self.method = method
		self.name = name.strip()
		self.uri = uri

	def getAditionalHeaders(self):
		return copy.deepcopy(self.aditionalHeaders)

	def getBody(self):
		return copy.deepcopy(self.body)

	def getContentType(self):
		return self.contentType

	def getMemo(self):
		return self.memo

	def getMethod(self):
		return self.method

	def getName(self):
		return self.name

	def getUri(self):
		return self.uri

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

def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください。")
	return ""

def validateUri(uri):
	assert isinstance(uri, str)
	uri = uri.strip()
	if not len(uri):
		return _("URIを入力してください。")
	return ""
