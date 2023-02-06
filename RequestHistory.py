# -*- coding: utf-8 -*-
# request History
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import history
import traceback

import constants
import globalVars
import simpleDialog

from logging import getLogger

from entities import Traffic

log = getLogger("%s.%s" % (constants.LOG_PREFIX, "requestHistory"))
DICT_KEY = "requestHistory"


class RequestHistory:
	def __init__(self, fileName, maxCount):
		self.fileName = fileName
		self.obj = history.History(maxCount)
		log.info("read history from %s" % fileName)
		try:
			self.obj.loadFile(fileName, DICT_KEY, True)
		except Exception as e:
			log.error(traceback.format_exc())
			traceback.print_exc()
			simpleDialog.errorDialog(_("リクエストログの読み込みに失敗しました。\n\n") + str(e), globalVars.app.hMainView.hFrame)

	def add(self, request):
		self.obj.add(request)
		try:
			self.obj.saveFile(self.fileName, DICT_KEY)
		except Exception as e:
			log.error(traceback.format_exc())
			traceback.print_exc()
			simpleDialog.errorDialog(_("リクエストログの保存に失敗しました。\n\n") + str(e), globalVars.app.hMainView.hFrame)

	def getList(self):
		return self.obj.getList()

	def setList(self, lst):
		assert type(lst) == list
		for item in lst:
			assert type(item) == Traffic.Traffic
		self.obj.setList(lst)
