# -*- coding: utf-8 -*-
# �g���t�B�b�N(���N�G�X�g+���X�|���X)�G���e�B�e�B
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import copy

from entities import Request,Response


class Traffic:
	def __init__(self, request,response):
		assert type(request) == Request.Request
		assert type(response) == Response.Response
		self.request = copy.deepcopy(request)
		self.response = copy.deepcopy(response)

	def getRequest(self):
		return self.request

	def getResponse(self):
		return self.response

	def toTreeData(self):
		return {
			"RequestInfo": {
				"headers": self.request.toHeaderDict(),
				"method": self.request.getMethod().name,
				"url": self.request.getUri(),
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

	# ���X�g�\���p����
	def GetListTuple(self):
		return self.request.getName(), self.response.getStatusCode(), self.request.getMemo()

	def __getitem__(self, index):
		return self.GetListTuple()[index]

	def __len__(self):
		return len(self.GetListTuple())

	def __setitem__(self, index, obj):
		raise NotImplementedError

