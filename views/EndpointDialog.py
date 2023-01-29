# -*- coding: utf-8 -*-
# エンドポイント一覧ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import menuItemsStore
import simpleDialog
import views.ViewCreator

from entities import Endpoint
from enumClasses import Method
from simpleDialog import errorDialog
from views.baseDialog import *
from views.EndpointEditDialog import *
from views.RequestEditDialog import *

class EndpointDialog(BaseDialog):
	def __init__(self):
		super().__init__("endpointDialog")
		self.result = None

	def Initialize(self, provider, parent):
		self.log.debug("created with" + provider.getName())
		self.provider = provider
		self.parent = parent
		super().Initialize(parent.wnd,_("エンドポイント一覧"))
		self.lst = provider.getEndpoints()
		self.InstallControls()
		return True

	def InstallControls(self):
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		(self.list,dummy) = self.creator.virtualListCtrl(_("設定中のエンドポイント"), size=(600,400))
		self.list.AppendColumn(_("名前"), width=300)
		self.list.AppendColumn(_("メモ"), width=300)
		self.list.setList(self.lst)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.onActivate)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.addButton = creator.button(_("追加(&A)"), self.add)
		self.editButton = creator.button(_("編集(&E)"), self.edit)
		self.deleteButton = creator.button(_("削除(&D)"), self.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT)
		self.bClose=creator.closebutton(_("閉じる(&C)"),None)

		self.ItemSelected()

		keymap = self.app.hMainView.menu.keymap
		keymap.Set(self.identifier,self.wnd,self.onKey)

	def ItemSelected(self,event=None):
		self.editButton.Enable(self.list.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.list.GetFocusedItem()>=0)

	def activate(self, target):
		d = RequestEditDialog()
		d.InitializeFromEndpoint(self, self.provider, target)
		if d.Show() == wx.ID_OK:
			self.result = d.GetValue()
			self.wnd.EndModal(wx.ID_EXECUTE)


	def add(self, event=None):
		d = EndpointEditDialog()
		d.Initialize(self.provider, Endpoint.Endpoint(self.provider, _("新規エンドポイント"), Method.GET, "/", [], []), self.wnd)
		if d.Show() == wx.ID_OK:
			self.list.Append(d.GetValue())
			self.save()

	def edit(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		d = EndpointEditDialog()
		d.Initialize(self.provider, target, self.wnd)
		result = d.Show()
		if result == wx.ID_OK:
			self.list[index] = d.GetValue()
			self.save()

	def delete(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]

		if simpleDialog.yesNoDialog(_("削除の確認"), _("%sを削除しますか？" % target.getName()), self.wnd) == wx.ID_YES:
			self.list.DeleteItem(index)
			self.save()

	def save(self):
		self.provider.setEndpoints(self.lst)
		self.parent.save()

	def onActivate(self, event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		self.activate(self.lst[index])

	def onKey(self, event):
		selected=event.GetId()#メニュー識別しの数値
		index = self.list.GetFocusedItem()
		if selected==menuItemsStore.getRef("ADD"):
			self.add()
			return
		elif index>=0:
			if selected==menuItemsStore.getRef("ACTIVATED"):
				self.activate(self.lst[index])
			elif selected==menuItemsStore.getRef("DELETE"):
				self.delete()
				return
			elif selected==menuItemsStore.getRef("EDIT"):
				self.edit()
				return
		event.Skip()

	def GetData(self):
		return self.result
