# -*- coding: utf-8 -*-
#Application Main

import sys
import wx

import AppBase
import commandParser
import constants
import globalVars
import proxyUtil
import RequestHistory
import update

from RequestSender import RequestSender


class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		self.setGlobalVars()
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		# アップデートを実行
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)

		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.hMainView.Show()
		wx.YieldIfNeeded()

		# 履歴モジュール
		globalVars.history = RequestHistory.RequestHistory(constants.HISTORY_FILE_NAME, self.config.getint("general", "histry_max", 0,100,100))

		# コマンドのパース
		if not self.hMainView.isLoaded() and len(sys.argv) >= 2:
			parser = commandParser.CommandParser()
			self.hMainView.showData(RequestSender.send(parser.parse_args()))
			# エラーになったらここにはこないで終了されてしまう			
		return True

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0
