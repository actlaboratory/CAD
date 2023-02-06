# -*- coding: utf-8 -*-
# レスポンスエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy
import datetime

from .BodyField import BodyField
from .Header import Header


class Response:
	def __init__(self, statusCode, ellapsed, headers=[], body=[], memo=""):
		if (validateStatusCode(statusCode) or
			validateEllapsed(ellapsed) or
			validateHeaders(headers) or
			validateBody(body) or
			validateMemo(memo)):
			raise ValueError()

		self.body = copy.deepcopy(body)
		if type(ellapsed) == datetime.timedelta:
			self.ellapsed = ellapsed.seconds + (ellapsed.microseconds / 1000000)
		else:
			self.ellapsed = ellapsed
		self.headers = copy.deepcopy(headers)
		self.memo = memo.strip()
		self.statusCode = statusCode

	def getBody(self):
		return copy.deepcopy(self.body)

	def getEllapsed(self):
		return self.ellapsed

	def getHeaders(self):
		return copy.deepcopy(self.headers)

	def getMemo(self):
		return self.memo

	def getStatusCode(self):
		return self.statusCode

	# リスト表示用項目
	def GetListTuple(self):
		return self.statusCode, self.memo

	def toHeaderDict(self):
		headerDict = {}
		for i in self.headers:
			headerDict[i.getName()] = i.getValue()
		return headerDict

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError

def validateBody(body):
	assert type(body) == dict or type(body) == str
	return ""

def validateEllapsed(ellapsed):
	if type(ellapsed) == datetime.timedelta:
		if ellapsed.days != 0 or ellapsed.seconds<0 or ellapsed.microseconds<0:
			return _("値が無効です。")
	elif  type(ellapsed) == float:
		if ellapsed<0:
			return _("値が無効です。")
	elif ellapsed is None:
		pass
	else:
		assert False
	return ""

def validateHeaders(headers):
	assert type(headers) == list
	for item in headers:
		assert type(item) == Header

def validateMemo(memo):
	assert isinstance(memo, str)
	return ""

def validateStatusCode(statusCode):
	assert isinstance(statusCode, int) or statusCode is None
	if statusCode is not None and (statusCode <= 100 or statusCode >= 1000):
		return _("ステータスコードは100から999までの値である必要があります。")
	return ""
