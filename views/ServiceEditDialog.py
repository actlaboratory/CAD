# -*- coding: utf-8 -*-
# サービス設定

import wx
import globalVars
import views.ViewCreator
import wx.lib.scrolledpanel
import views.KeyValueSettingArea
import constants
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("ServiceEditDialog")

	def Initialize(self, service, parent=None):
		self.log.debug("created")
		if parent == None:
			self.app.hMainView.hFrame
		super().Initialize(parent,_("サービス編集"))
		self.InstallControls(service)
		return True

	def InstallControls(self, service):
		"""いろんなwidgetを設置する。"""

		# 画面をスクロール可能にする
		panel = wx.lib.scrolledpanel.ScrolledPanel(self.panel,wx.ID_ANY, size=(850,500))
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,None,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		sizer = creator.GetSizer()
		self.sizer.Add(panel,1,wx.EXPAND)

		grid=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,views.ViewCreator.FlexGridSizer,20,2)

		# 設定につける名前
		self.name, dummy = grid.inputbox(_("名前"), None, service["name"], wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.name.hideScrollBar(wx.HORIZONTAL)

		# 通信形式
		self.contentType, dummy = grid.combobox(_("通信形式"), ["application/json","application/x-www-form-urlencoded"], None, state=0)

		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)

		# ベースURI
		self.baseUri = views.KeyValueSettingArea.KeyValueSettingArea(
			"baseUri",
			BaseUriSettingDialog,
			[
				(_("名前"), 0, 200),
				(_("アドレス"), 0, 500),
				(_("ポート"),0, 50)
			],
			{},
			{},
		)
		self.baseUri.Initialize(self.wnd, creator, _("ヘッダ"))

		# 共通ヘッダ
		self.headers = views.KeyValueSettingArea.KeyValueSettingArea(
			"headers",
			HeaderSettingDialog,
			[
				(_("フィールド名"), 0, 200),
				(_("値の種類"), 0, 200),
				(_("値"),0, 300)
			],
			{},
			{},
		)
		self.headers.Initialize(self.wnd, creator, "URI")

		self.memo,dummy = creator.inputbox(_("メモ"), None, service["memo"], wx.TE_MULTILINE|wx.BORDER_RAISED, 500, sizerFlag=wx.EXPAND|wx.ALL)
		self.memo.hideScrollBar(wx.HORIZONTAL)

		hCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL|wx.ALIGN_RIGHT,margin=20)
		closeButton=hCreator.okbutton(_("OK"))
		cancelButton=hCreator.cancelbutton(_("キャンセル"))

		panel.SetupScrolling()

	def addHost(self,event):
		pass
	def editHost(self,event):
		pass
	def addHeaders(self,event):
		pass
	def editHeaders(self,event):
		pass

	def processEnter(self,event):
		self.wnd.EndModal(wx.OK)

class HeaderSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""ヘッダの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=constants.HEADER_TYPE_CONST, body=""):
		super().__init__(
			parent,
			[
				(_("フィールド名"), True),
				(_("タイプ"), (_("固定値"), _("編集可能"))),
				(_("値"), True),
			],
			[None]*3,
			key,headerType,body
		)

	def Initialize(self):
		return super().Initialize(_("ヘッダ設定"))


class BaseUriSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	def __init__(self, parent, key="", uri="", port=""):
		super().__init__(
			parent,
			[
				(_("名前"), True),
				(_("アドレス"), True),
				(_("ポート番号"), True),
			],
			[None]*3,
			key, uri, port
		)

	def Initialize(self):
		return super().Initialize(_("ベースURI設定"))
