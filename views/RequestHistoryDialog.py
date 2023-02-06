# -*- coding: utf-8 -*-
# リクエスト履歴ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import menuItemsStore

import simpleDialog
import views.ViewCreator

from views.baseDialog import *


class RequestHistoryDialog(BaseDialog):
	def __init__(self):
		super().__init__("RequestHistoryDialog")
		self.lst = self.load()
		self.target = None

	def Initialize(self, parent=None):
		self.log.debug("created")
		if parent == None:
			parent = self.app.hMainView.hFrame
		super().Initialize(parent,_("リクエスト履歴一覧"))
		self.InstallControls()
		return True

	def InstallControls(self):
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		(self.list,dummy) = self.creator.virtualListCtrl(_("リクエスト履歴"), size=(600,400))
		self.list.AppendColumn(_("名前"), width=300)
		self.list.AppendColumn(_("ステータス"), width=300)
		self.list.AppendColumn(_("メモ"), width=300)
		self.list.setList(self.lst)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.onActivate)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.reuseButton = creator.button(_("再利用(&R)"), self.reuse)
		self.editButton = creator.button(_("編集(&E)"), self.edit)
		self.deleteButton = creator.button(_("削除(&D)"), self.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT)
		self.bClose=creator.closebutton(_("閉じる(&C)"),None)

		self.ItemSelected()

		keymap = self.app.hMainView.menu.keymap
		keymap.Set(self.identifier,self.wnd,self.onKey)

	def ItemSelected(self,event=None):
		self.reuseButton.Enable(self.list.GetFocusedItem()>=0)
		self.editButton.Enable(self.list.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.list.GetFocusedItem()>=0)

	def activate(self, target):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		self.target = target
		self.wnd.EndModal(wx.ID_VIEW_DETAILS)

	def reuse(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		return

	def edit(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		return

	def delete(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]

		if simpleDialog.yesNoDialog(_("削除の確認"), _("%sを削除しますか？" % target.getRequest().getName()), self.wnd) == wx.ID_YES:
			self.list.DeleteItem(index)
			self.save()

	def load(self):
		return globalVars.history.getList()

	def save(self):
		globalVars.history.setList(self.lst)

	def onActivate(self, event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		self.activate(self.lst[index])

	def onKey(self, event):
		selected=event.GetId()#メニュー識別しの数値
		index = self.list.GetFocusedItem()
		if selected==menuItemsStore.getRef("REUSE"):
			self.add()
			return
		elif selected==menuItemsStore.getRef("ACTIVATED"):
			return self.activate(self.lst[index])
		elif selected==menuItemsStore.getRef("DELETE"):
			return self.delete()
		elif selected==menuItemsStore.getRef("EDIT"):
			return self.edit()
		event.Skip()

	def GetData(self):
		if self.target:
			return self.target.toTreeData()
		else:
			return None
