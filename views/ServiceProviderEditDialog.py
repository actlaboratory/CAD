# -*- coding: utf-8 -*-
# サービスプロバイダ設定ダイアログ

import wx
import wx.lib.scrolledpanel

import simpleDialog
import views.KeyValueSettingArea
import views.ViewCreator

from dao.ServiceProviderDao import ServiceProviderDao

from enumClasses import ContentType
from enumClasses import HeaderFieldType

from entities import BaseUri
from entities import Header
from entities import ServiceProvider

from simpleDialog import errorDialog
from views.baseDialog import *


class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("ServiceProviderDialog")
		self.lst = self.load()

	def Initialize(self, parent=None):
		self.log.debug("created")
		if parent == None:
			parent = self.app.hMainView.hFrame
		super().Initialize(parent,_("サービスプロバイダ一覧"))
		self.InstallControls()
		return True

	def InstallControls(self):
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		(self.list,dummy) = self.creator.virtualListCtrl(_("設定中のプロバイダ"), size=(600,400))
		self.list.AppendColumn(_("サービス名"), width=300)
		self.list.AppendColumn(_("メモ"), width=300)
		self.list.setList(self.lst)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.addButton = creator.button(_("追加"), self.add)
		self.editButton = creator.button(_("編集"), self.edit)
		self.deleteButton = creator.button(_("削除"), self.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.bOk=creator.okbutton(_("ＯＫ"),self.apply)
		self.bCancel=creator.cancelbutton(_("キャンセル"),None)

		self.ItemSelected()

	def ItemSelected(self,event=None):
		self.editButton.Enable(self.list.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.list.GetFocusedItem()>=0)

	def add(self, event):
		d = EditDialog()
		d.Initialize(ServiceProvider.ServiceProvider(_("新規プロバイダ"), ContentType.JSON), self.wnd)
		if d.Show() == wx.ID_OK:
			self.list.Append(d.GetValue())

	def edit(self, event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		d = EditDialog()
		d.Initialize(target, self.wnd)
		result = d.Show()
		if result == wx.ID_OK:
			self.list[index] = d.GetValue()

	def delete(self, event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]

		if simpleDialog.yesNoDialog(_("削除の確認"), _("%sを削除しますか？" % target.getName()), self.wnd) == wx.ID_YES:
			self.list.DeleteItem(index)

	def apply(self, event):
		try:
			ServiceProviderDao.saveAll(self.lst)
			event.Skip()
		except Exception as e:
			simpleDialog.dialog(_("エラー"), _("保存に失敗しました。\n\n") + str(e))

	def load(self):
		try:
			return ServiceProviderDao.loadAll()
		except Exception as e:
			simpleDialog.dialog(_("エラー"), _("読込に失敗しました。\n\n") + str(e))
			return []

class EditDialog(BaseDialog):
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
		tmp1 = {}
		tmp2 = {}
		for i in self.provider.getBaseUris():
			tmp1[i.getName()] = i.getAddress()
			tmp2[i.getName()] = i.getPort()

		self.baseUri = views.KeyValueSettingArea.KeyValueSettingArea(
			"baseUri",
			BaseUriSettingDialog,
			[
				(_("名前"), 0, 200),
				(_("アドレス"), 0, 450),
				(_("ポート"),0, 50)
			],
			tmp1,
			tmp2,
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
		ports = list(values[1].values())
		for i in range(len(names)):
			baseUri.append(BaseUri.BaseUri(names[i], addresses[i], ports[i]))

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

class HeaderSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""ヘッダの設定内容を入力するダイアログ"""

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

		error = Header.validateValue(self.edits[2].GetValue())
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


class BaseUriSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	def __init__(self, parent, key="", uri="https://", port="443"):
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

	def Validation(self,event):
		error = BaseUri.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BaseUri.validateAddress(self.edits[1].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BaseUri.validatePort(self.edits[2].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetValue().strip(),
			self.edits[2].GetValue().strip()
		]
