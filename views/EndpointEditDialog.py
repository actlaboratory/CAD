# -*- coding: utf-8 -*-
# エンドポイント設定ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import simpleDialog
import views.KeyValueSettingArea
import views.ViewCreator

from entities import BodyField, Endpoint, Header, UriField
from enumClasses import BodyFieldType, ContentType, Method, UriFieldType
from simpleDialog import errorDialog
from views.baseDialog import *


class EndpointEditDialog(BaseDialog):
	def __init__(self):
		super().__init__("EndpointEditDialog")

	def Initialize(self, provider, endpoint, parent):
		self.log.debug("created")
		super().Initialize(parent,_("エンドポイント編集"))
		self.provider = provider
		self.endpoint = endpoint
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
		self.name, dummy = grid.inputbox(_("名前"), None, self.endpoint.getName(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.name.hideScrollBar(wx.HORIZONTAL)

		# メソッド
		self.method, dummy = grid.combobox(_("メソッド"), [item.name for item in Method], None, state=self.endpoint.getMethod().value)

		# URI
		self.uri, dummy = grid.inputbox(_("URI"), None, self.endpoint.getUri(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.uri.hideScrollBar(wx.HORIZONTAL)

		# URIフィールド
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		tmp1 = {}
		tmp2 = {}
		for i in self.endpoint.getUriFields():
			tmp1[i.getName()] = i.getFieldType().view_name
			tmp2[i.getName()] = i.getValue()

		self.uriFields = views.KeyValueSettingArea.KeyValueSettingArea(
			"uriField",
			UriFieldSettingDialog,
			[
				(_("名前"), 0, 200),
				(_("値の種類"), 0, 200),
				(_("値"),0, 300)
			],
			tmp1,
			tmp2,
		)
		self.uriFields.Initialize(self.wnd, creator, _("Uriフィールド"))

		# bodyフィールド
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		tmp1 = {}
		tmp2 = {}
		for i in self.endpoint.getBody():
			tmp1[i.getName()] = i.getFieldType().view_name
			tmp2[i.getName()] = i.getValue()

		self.bodyFields = views.KeyValueSettingArea.KeyValueSettingArea(
			"Body",
			BodyFieldSettingDialog,
			[
				(_("名前"), 0, 200),
				(_("値の種類"), 0, 200),
				(_("値"),0, 300)
			],
			tmp1,
			tmp2,
		)
		self.bodyFields.Initialize(self.wnd, creator, _("Body"))

		# 通信形式
		grid=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,views.ViewCreator.FlexGridSizer,20,2)
		self.contentType, dummy = grid.combobox(_("通信形式"), [_("サービスプロバイダの規定値"), "application/json","application/x-www-form-urlencoded"], None, state=((self.endpoint.getContentType().value +1) if self.endpoint.getContentType() is not None else 0))

		# 追加ヘッダ
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		tmp1 = {}
		tmp2 = {}
		for i in self.endpoint.getAditionalHeaders():
			tmp1[i.getName()] = i.getFieldType().view_name
			tmp2[i.getName()] = i.getValue()

		self.aditionalHeaders = views.KeyValueSettingArea.KeyValueSettingArea(
			"aditionalHeaders",
			AditionalHeaderSettingDialog,
			[
				(_("フィールド名"), 0, 200),
				(_("値の種類"), 0, 200),
				(_("値"),0, 300)
			],
			tmp1,
			tmp2,
		)
		self.aditionalHeaders.Initialize(self.wnd, creator, _("追加ヘッダ"))

		self.memo,dummy = creator.inputbox(_("メモ"), None, self.endpoint.getMemo(), wx.TE_MULTILINE|wx.BORDER_RAISED, 500, sizerFlag=wx.EXPAND|wx.ALL)
		self.memo.hideScrollBar(wx.HORIZONTAL)

		hCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL|wx.ALIGN_RIGHT,margin=20)
		okButton=hCreator.okbutton(_("OK"), self.processEnter)
		cancelButton=hCreator.cancelbutton(_("キャンセル"))

		panel.SetupScrolling()

	def processEnter(self,event):
		error = Endpoint.validateName(self.name.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = Endpoint.validateUri(self.uri.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return


		uriFields = []
		values = self.uriFields.GetValue()
		names = list(values[0].keys())
		fieldTypes = list(values[0].values())
		values = list(values[1].values())
		for i in range(len(names)):
			uriFields.append(UriField.UriField(names[i], UriFieldType[fieldTypes[i]], values[i]))
		error = Endpoint.validateUriFields(self.uri.GetValue(), uriFields)
		if error:
			errorDialog(error, self.wnd)
			return

		error = Endpoint.validateMemo(self.memo.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		self.wnd.EndModal(wx.ID_OK)

	def GetData(self):
		uriFields = []
		values = self.uriFields.GetValue()
		names = list(values[0].keys())
		fieldTypes = list(values[0].values())
		values = list(values[1].values())
		for i in range(len(names)):
			uriFields.append(UriField.UriField(names[i], UriFieldType[fieldTypes[i]], values[i]))

		bodyFields = []
		values = self.bodyFields.GetValue()
		names = list(values[0].keys())
		fieldTypes = list(values[0].values())
		values = list(values[1].values())
		for i in range(len(names)):
			bodyFields.append(BodyField.BodyField(names[i], BodyFieldType[fieldTypes[i]], values[i]))

		headers = []
		values = self.aditionalHeaders.GetValue()
		names = list(values[0].keys())
		fieldTypes = list(values[0].values())
		values = list(values[1].values())
		for i in range(len(names)):
			headers.append(Header.Header(names[i], HeaderFieldType[fieldTypes[i]], values[i]))

		return Endpoint.Endpoint(
			self.provider,
			self.name.GetValue().strip(),
			Method(self.method.GetSelection()),
			self.uri.GetValue().strip(),
			uriFields,
			bodyFields,
			ContentType(self.contentType.GetSelection() - 1) if self.contentType.GetSelection() > 0 else None,
			headers,
			self.memo.GetValue().strip()
		)

class AditionalHeaderSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""追加ヘッダの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
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

	def Validation(self,event):
		error = Header.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = Header.validateValue(HeaderFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetStringSelection(),
			self.edits[2].GetValue().strip()
		]


class BodyFieldSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""Bodyの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
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

	def Validation(self,event):
		error = BodyField.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BodyField.validateValue(BodyFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetStringSelection(),
			self.edits[2].GetValue().strip()
		]

class UriFieldSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""Uriフィールドの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
		super().__init__(
			parent,
			[
				(_("フィールド名"), True),
				(_("タイプ"), (_("編集可能"),)),
				(_("値"), True),
			],
			[None]*3,
			key,headerType,body
		)

	def Initialize(self):
		return super().Initialize(_("ヘッダ設定"))

	def Validation(self,event):
		error = UriField.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = UriField.validateValue(UriFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetStringSelection(),
			self.edits[2].GetValue().strip()
		]

