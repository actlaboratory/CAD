# -*- coding: utf-8 -*-
# リクエスト履歴ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import pyperclip
import wx

import menuItemsStore
import RequestSender
import simpleDialog
import views.ViewCreator
import views.RequestEditDialog

from views.base import BaseMenu
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
		self.createPopupMenu()
		return True

	def InstallControls(self):
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		(self.list,dummy) = self.creator.virtualListCtrl(_("リクエスト履歴"), size=(600,400))
		self.list.AppendColumn(_("名前"), width=300)
		self.list.AppendColumn(_("ステータス"), width=100)
		self.list.AppendColumn(_("メモ"), width=200)
		self.list.AppendColumn(_("送信日時"), width=100)
		self.list.setList(self.lst)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.onActivate)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)


		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.reuseButton = creator.button(_("再利用(&R)"), self.reuse)
		self.editButton = creator.button(_("編集(&E)"), self.edit)
		self.deleteButton = creator.button(_("削除(&D)"), self.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT)
		self.bClose=creator.closebutton(_("閉じる(&C)"),None)

		self.ItemSelected()

		keymap = self.app.hMainView.menu.keymap
		keymap.Set(self.identifier,self.list,self.onCommand)

	def ItemSelected(self,event=None):
		self.reuseButton.Enable(self.list.GetFocusedItem()>=0)
		self.editButton.Enable(self.list.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.list.GetFocusedItem()>=0)

	def createPopupMenu(self):
		self.menu = BaseMenu(self.identifier)

		self.popupMenu = wx.Menu()
		self.menu.RegisterMenuCommand(self.popupMenu,{
			"HISTORY_COPY_CURL_COMMAND": self.copyCurlCommand,
			"HISTORY_VIEW": self.onActivate,
			"HISTORY_REUSE": self.reuse,
			"HISTORY_EDIT": self.edit,
			"HISTORY_DELETE": self.delete,

		})

	def activate(self, target):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		self.target = target.toTreeData()
		self.wnd.EndModal(wx.ID_VIEW_DETAILS)

	def reuse(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		self.target = RequestSender.RequestSender.send(target.getRequest()).toTreeData()
		self.wnd.EndModal(wx.ID_VIEW_DETAILS)

	def edit(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index].getRequest()
		d = views.RequestEditDialog.RequestEditDialog()
		d.InitializeFromRequest(self.wnd,target)
		if d.Show() == wx.ID_CANCEL:
			return
		self.target = RequestSender.RequestSender.send(d.GetData()).toTreeData()
		self.wnd.EndModal(wx.ID_VIEW_DETAILS)
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

	def onCommand(self, event):
		selected=event.GetId()#メニュー識別しの数値
		callback = self.menu.getCallback(selected)
		if callback:
			callback(event)
			return

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

	def onContextMenu(self,event):
		if self.list.GetFocusedItem() < 0:
			return
		self.list.PopupMenu(self.popupMenu,event)


	def copyCurlCommand(self,event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]

		pyperclip.copy(target.getRequest().toCurlCommand())

	def GetData(self):
		return self.target
