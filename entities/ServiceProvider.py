# -*- coding: utf-8 -*-
# サービスプロバイダエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy

from enumClasses import ContentType
from .Header import Header
from .BaseUri import BaseUri
from .Endpoint import Endpoint

class ServiceProvider:

	def __init__(self, name, contentType, baseUris=[], headers=[], memo=""):
		if (validateName(name) or
			type(contentType) != ContentType or
			validateBaseUri(baseUris) or
			validateHeaders(headers) or
			validateMemo(memo)):
			raise ValueError()
		self.baseUris = copy.deepcopy(baseUris)
		self.contentType = contentType
		self.headers = copy.deepcopy(headers)
		self.memo = memo.strip()
		self.name = name.strip()

		self.endpoints = []

	def getBaseUris(self):
		return self.baseUris

	def getContentType(self):
		return self.contentType

	def getEndpoints(self):
		return self.endpoints

	def getHeaders(self):
		return self.headers

	def getMemo(self):
		return self.memo

	def getName(self):
		return self.name

	# リスト表示用項目
	def GetListTuple(self):
		return self.name, self.memo

	def setEndpoints(self, lst):
		if validateEndpoints(lst):
			raise ValueError()
		self.endpoints = copy.deepcopy(lst)

	def updateEdit(self, other):
		"""
			基本項目をotherの内容に更新する
		"""
		self.baseUris = copy.deepcopy(other.baseUris)
		self.contentType = other.contentType
		self.headers = copy.deepcopy(other.headers)
		self.memo = other.memo
		self.name = other.name
		return self

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError


def validateBaseUri(baseUri):
	assert type(baseUri) == list
	for item in baseUri:
		assert type(item) == BaseUri

def validateEndpoints(endpoints):
	assert type(endpoints) == list
	for item in endpoints:
		assert type(item) == Endpoint

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
