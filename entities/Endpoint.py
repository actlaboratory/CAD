# -*- coding: utf-8 -*-
# エンドポイントエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy
import re

from enumClasses import ContentType, Method
from .BodyField import BodyField
from .Header import Header
from .UriField import UriField

from urllib3.util.url import parse_url

class Endpoint:

	def __init__(self, parent, name, method, uri, uriFields, body, contentType=None, headers=[], memo=""):
		if (
			validateName(name) or
			type(method) is not Method or
			validateUri(uri) or
			validateUriFields(uri, uriFields) or
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
		self.uriFields = uriFields

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

	def getUriFields(self):
		return self.uriFields

	# リスト表示用項目
	def GetListTuple(self):
		return self.name, self.memo

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError

def getNeedFieldsFromUri(uri):
	"""
		Uriを完成させるために指定が必要なフィールド名の一覧を返す
	"""
	return re.findall(r"\{(.+?)\}", uri)

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
	try:
		url = parse_url(uri)
		if url.auth:
			return _("認証情報はアドレスではなくAuthorizationヘッダで指定してください。")
		elif url.scheme and not url.host:
			return _("アドレスにホスト名が含まれていません。")
		elif (not url.scheme) and url.port:
			return _("アドレスにポート番号を含められるのは、スキーム名を含めた完全なURIを入力する場合のみです。")

	except:
		import traceback
		traceback.print_exc()
		return _("アドレスが不正です。")
	return ""


def validateUriFields(uri, fields):
	assert type(fields) == list
	needs = getNeedFieldsFromUri(uri)
	for item in fields:
		assert type(item) == UriField
		if item.getName() not in needs:
			return _("Uriフィールド%sはUriの中で指定されていません。" % item.getName())
		needs.remove(item.getName())
	for item in needs:
		return _("uriフィールド%sは値が設定されていません。" % item)
	return ""
