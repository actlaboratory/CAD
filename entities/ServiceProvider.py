# -*- coding: utf-8 -*-
# サービスプロバイダエンティティ

from enumClasses import ContentType
from .Header import Header
from .BaseUri import BaseUri

class ServiceProvider:

	def __init__(self,name, contentType, baseUris=[], headers=[], memo=""):
		if (validateName(name) or
			type(contentType) != ContentType or
			validateBaseUri(baseUris) or
			validateHeaders(headers) or
			validateMemo(memo)):
			raise ValueError()
		self.baseUris = baseUris
		self.contentType = contentType
		self.headers = headers
		self.memo = memo.strip()
		self.name = name.strip()

	def getBaseUris(self):
		return self.baseUris

	def getContentType(self):
		return self.contentType

	def getHeaders(self):
		return self.headers

	def getMemo(self):
		return self.memo

	def getName(self):
		return self.name

	# リスト表示用項目
	def GetListTuple(self):
		return self.name, self.memo

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError


def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください。")
	return ""

def validateBaseUri(baseUri):
	assert type(baseUri) == list
	for item in baseUri:
		assert type(item) == BaseUri

def validateHeaders(headers):
	assert type(headers) == list
	for item in headers:
		assert type(item) == Header


def validateMemo(memo):
	assert isinstance(memo, str)
