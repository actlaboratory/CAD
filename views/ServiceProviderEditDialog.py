# -*- coding: utf-8 -*-
# サービスプロバイダ設定ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import simpleDialog
import views.KeyValueSettingArea
import views.ViewCreator

from enumClasses import ContentType
from enumClasses import HeaderFieldType

from entities import BaseUri
from entities import Header
from entities import ServiceProvider

from simpleDialog import errorDialog
from views.baseDialog import *
from views.HeaderSettingDialog import *


class ServiceProviderEditDialog(BaseDialog):
	def __init__(self):
		super().__init__("ServiceProviderEditDialog")

	def Initialize(self, provider, parent):
		self.log.debug("created")
		super().Initialize(parent,_("サービスプロバイダ編集"))
		self.provider = provider
		self.InstallControls()
		return True

	def InstallControls(self):
		# 画面をスクロール可能にする
		panel = wx.lib.scrolledpanel.ScrolledPanel(self.panel,wx.ID_ANY, size=(850,500))
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,None,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		sizer = creator.GetSizer()
		self.sizer.Add(panel,1,wx.EXPAND)

		grid=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,views.ViewCreator.FlexGridSizer,20,2)

		# 設定につける名前
		self.name, dummy = grid.inputbox(_("名前"), None, self.provider.getName(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.name.hideScrollBar(wx.HORIZONTAL)

		# 通信形式
		self.contentType, dummy = grid.combobox(_("通信形式"), ["application/json","application/x-www-form-urlencoded"], None, state=self.provider.getContentType().value)

		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)

		# ベースURI
		tmp = {}
		for i in self.provider.getBaseUris():
			tmp[i.getName()] = i.getAddress()

		self.baseUri = views.KeyValueSettingArea.KeyValueSettingArea(
			"baseUri",
			BaseUriSettingDialog,
			[
				(_("名前"), 0, 200),
				(_("アドレス"), 0, 450),
			],
			tmp,
		)
		self.baseUri.Initialize(self.wnd, creator, _("ベースURI"))

		# 共通ヘッダ
		tmp1 = {}
		tmp2 = {}
		for i in self.provider.getHeaders():
			tmp1[i.getName()] = i.getFieldType().view_name
			tmp2[i.getName()] = i.getValue()


		self.headers = views.KeyValueSettingArea.KeyValueSettingArea(
			"headers",
			HeaderSettingDialog,
			[
				(_("フィールド名"), 0, 200),
				(_("値の種類"), 0, 200),
				(_("値"),0, 300)
			],
			tmp1,
			tmp2,
		)
		self.headers.Initialize(self.wnd, creator, _("ヘッダ"))

		self.memo,dummy = creator.inputbox(_("メモ"), None, self.provider.getMemo(), wx.TE_MULTILINE|wx.BORDER_RAISED, 500, sizerFlag=wx.EXPAND|wx.ALL)
		self.memo.hideScrollBar(wx.HORIZONTAL)

		hCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL|wx.ALIGN_RIGHT,margin=20)
		okButton=hCreator.okbutton(_("OK"), self.processEnter)
		cancelButton=hCreator.cancelbutton(_("キャンセル"))

		panel.SetupScrolling()

	def processEnter(self,event):
		error = ServiceProvider.validateName(self.name.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = ServiceProvider.validateMemo(self.memo.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		self.wnd.EndModal(wx.ID_OK)

	def GetData(self):
		baseUri = []
		values = self.baseUri.GetValue()
		names = list(values[0].keys())
		addresses = list(values[0].values())
		for i in range(len(names)):
			baseUri.append(BaseUri.BaseUri(names[i], addresses[i]))

		headers = []
		values = self.headers.GetValue()
		names = list(values[0].keys())
		fieldTypes = list(values[0].values())
		values = list(values[1].values())
		for i in range(len(names)):
			headers.append(Header.Header(names[i], HeaderFieldType[fieldTypes[i]], values[i]))

		return ServiceProvider.ServiceProvider(
			self.name.GetValue().strip(),
			ContentType(self.contentType.GetSelection()),
			baseUri,
			headers,
			self.memo.GetValue().strip()
		)

class BaseUriSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	def __init__(self, parent, key="", uri="https://"):
		super().__init__(
			parent,
			[
				(_("名前"), True),
				(_("アドレス"), True),
			],
			[None]*3,
			key, uri
		)

	def Initialize(self):
		return super().Initialize(_("ベースURI設定"))

	def Validation(self,event):
		error = BaseUri.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BaseUri.validateAddress(self.edits[1].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetValue().strip(),
		]
