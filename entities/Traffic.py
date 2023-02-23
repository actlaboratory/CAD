# -*- coding: utf-8 -*-
# トラフィック(リクエスト+レスポンス)エンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy
import datetime

from entities import Request,Response


class Traffic:
	def __init__(self, request,response, requested_at):
		assert type(request) == Request.Request
		assert type(response) == Response.Response
		assert type(requested_at) == datetime.datetime
		self.request = copy.deepcopy(request)
		self.response = copy.deepcopy(response)
		self.requested_at = requested_at

	def getRequest(self):
		return self.request

	def getResponse(self):
		return self.response

	def toTreeData(self):
		return {
			"RequestInfo": {
				"url": self.request.getUri(),
				"method": self.request.getMethod().name,
				"headers": self.request.toHeaderDict(),
				"requested_at": self.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
			},
			"RequestBody": self.request.toBodyDict(),
			"ResponseInfo": {
				"status_code": self.response.getStatusCode(),
				"reason": self.response.getMemo(),
				"elapsed": self.response.getEllapsed(),
				"headers": self.response.toHeaderDict(),
			},
			"ResponseBody": self.response.getBody(),
		}

	# リスト表示用項目
	def GetListTuple(self):
		return self.request.getName(), self.response.getStatusCode(), self.request.getMemo(), self.requested_at

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError

