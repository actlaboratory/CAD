# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import collections.abc
import json
import sys
import wx

import constants
import errorCodes
import globalVars
import menuItemsStore

from chardet.universaldetector import UniversalDetector

from .base import *
from RequestSender import RequestSender
from simpleDialog import *

from views import globalKeyConfig
from views import settingsDialog
from views import versionDialog
from views import RequestEditDialog
from views import RequestHistoryDialog
from views import ServiceProviderDialog

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800,400),
			self.app.config.getint(self.identifier,"sizeY",600,300),
			self.app.config.getint(self.identifier,"positionX",50,0),
			self.app.config.getint(self.identifier,"positionY",50,0)
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.HORIZONTAL,style=wx.ALL|wx.EXPAND,proportion=1,space=0)
		self.tree,dummy = creator.treeCtrl("tree",self.events.OnTreeSelChanged,sizerFlag=wx.EXPAND,proportion=1,textLayout=None)
		self.lst,dummy = creator.listCtrl("values",sizerFlag=wx.EXPAND,proportion=1,textLayout=None)

		self.lst.AppendColumn("Key", format=wx.LIST_FORMAT_LEFT, width=150)
		self.lst.AppendColumn("Value", format=wx.LIST_FORMAT_LEFT, width=150)
		self.lst.AppendColumn("type", format=wx.LIST_FORMAT_LEFT, width=150)

		self.lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.events.OnListItemActivated, )
		self.lst.Bind(wx.EVT_LIST_KEY_DOWN, self.events.OnListKeyDown)
		self.tree.Bind(wx.EVT_TREE_KEY_DOWN, self.events.OnTreeKeyDown)

		self.load()
		self.tree.ExpandAll()

	def load(self):
		argv = sys.argv
		self.data={}
		if len(argv) == 2:
			# 指定されたファイルから
			with open(argv[1], 'rb') as fp:
				try:
					self.data = json.load(fp,strict=False)
				except json.decoder.JSONDecodeError as ex:
					fp.seek(0)
					self.data["file"] = fp.read().decode(encoding=self.getTextEncoding(fp),errors="replace")
		else:
			# 標準入力に何もない
			if sys.stdin.isatty():
				return

			# 標準入力から
			input = sys.stdin.read()
			if not self.input:
				return
			try:
				self.data = json.loads(input,strict=False)
			except json.decoder.JSONDecodeError as ex:
				self.data["input"] = input
		self.showData()

	# self.dataに入れたものを表示する
	def showData(self):
		self.tree.DeleteAllItems()
		root = self.tree.AddRoot('Root')
		self.tree.SetItemData(root, self.data)
		if isinstance(self.data, collections.abc.MutableMapping):
			for key, value in self.data.items():
				self.setTreeData(root, key, value)
		elif type(self.data) == list:
			for i in range(len(self.data)):
				self.setTreeData(root, '[{}]'.format(i), self.data[i])
		else:
			errorDialog("Data type miss match", self.wnd)
		self.visitor = TreeVisitor(self.tree, self.lst)
		self.visitor.visit_node(root)

	def setTreeData(self, node: wx.TreeItemId, key, value):
		id = self.tree.AppendItem(node, key)
		self.tree.SetItemData(id, value)
		if isinstance(value, collections.abc.MutableMapping):
			for k, v in value.items():
				self.setTreeData(id, k, v)
		elif isinstance(value, list):
			for i in range(len(value)):
				self.setTreeData(id, '[{}]'.format(i), value[i])

	def getTextEncoding(self,f):
		self.log.info("use detector")
		f.seek(0)
		detector = UniversalDetector()
		for binary in f:
			detector.feed(binary)
			if detector.done:
				break
		detector.close()
		f.seek(0)
		self.log.info("encoding = " + detector.result['encoding'])
		if not detector.result['encoding']:
			self.log.info("failed to detect. return utf-8")
			return "utf-8"
		return detector.result['encoding']

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""
		events = self.parent.events

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hOptionMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,{
			"FILE_SERVICE_PROVIDER" : events.serviceProvider,
			"FILE_NEW_REQUEST" : events.newRequest,
			"FILE_REQUEST_HISTORY" : events.requestHistory,
		})

		self.RegisterMenuCommand(self.hOptionMenu,{
			"OPTION_OPTION" : events.option,
			"OPTION_KEY_CONFIG" : events.keyConfig,
		})

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,{
			"HELP_UPDATE" : events.update,
			"HELP_VERSIONINFO" : events.versionInfo,
		})

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル"))
		self.hMenuBar.Append(self.hOptionMenu,_("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def serviceProvider(self, event):
		d = ServiceProviderDialog.Dialog()
		d.Initialize()
		if d.Show() == wx.ID_EXECUTE:
			data = RequestSender.send(d.GetValue())
			self.parent.data = data
			self.parent.showData()

	def newRequest(self, event):
		d = RequestEditDialog.RequestEditDialog()
		d.InitializeNewRequest(self.parent.hFrame)
		if d.Show() == wx.ID_OK:
			data = RequestSender.send(d.GetValue())
			self.parent.data = data
			self.parent.showData()

	def requestHistory(self, event):
		d = RequestHistoryDialog.RequestHistoryDialog()
		d.Initialize()
		result = d.Show()
		if result== wx.ID_VIEW_DETAILS:
			self.parent.data = d.GetValue()
			self.parent.showData()
		elif result == wx.ID_RETRY:
			pass

	def option(self, event):
		d = settingsDialog.Dialog()
		d.Initialize()
		d.Show()

	def keyConfig(self, event):
		if self.setKeymap(self.parent.identifier,_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
			#ショートカットキーの変更適用とメニューバーの再描画
			self.parent.menu.InitShortcut()
			self.parent.menu.ApplyShortcut(self.parent.hFrame)
			self.parent.menu.Apply(self.parent.hFrame)

	def update(self, event):
		globalVars.update.update()

	def versionInfo(self, event):
		d = versionDialog.dialog()
		d.Initialize()
		r = d.Show()


	def setKeymap(self, identifier,ttl, keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		d=globalKeyConfig.Dialog(keyData,menuData,[],filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		newMap.write()
		return True

	def OnTreeSelChanged(self,event):
		item = event.GetItem()
		self.parent.visitor.visit_node(item)

	def OnListItemActivated(self,event):
		item = event.GetItem()
		self.parent.visitor.visit_item(item)

	def OnListKeyDown(self,event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_BACK:
			self.parent.visitor.visit_parent()
		else:
			event.Skip()

	def OnTreeKeyDown(self,event):
		keycode = event.GetKeyCode()
		if keycode == ord('.'):
			self.parent.visitor.visit_first_child()
		else:
			event.Skip()


class TreeVisitor:
	def __init__(self, tree, lst):
		self.tree = tree
		self.lst = lst
		self.node = None

	def visit_node(self, node):
		if node != self.node:
			self.tree.SelectItem(node)
		self.node = node
		data = self.tree.GetItemData(self.node)
		self.fill_list(data)

	def visit_parent(self):
		parent = self.tree.GetItemParent(self.node)
		if parent.IsOk():
			self.visit_node(parent)

	def visit_first_child(self):
		child, cookie = self.tree.GetFirstChild(self.node)
		if child.IsOk():
			self.visit_node(child)

	def visit_item(self, item: wx.ListItem):
		name = item.GetText()
		child, cookie = self.tree.GetFirstChild(self.node)
		while child.IsOk():
			if self.tree.GetItemText(child) == name:
				break
			else:
				child, cookie = self.tree.GetNextChild(child, cookie)
		if child.IsOk():
			self.tree.SelectItem(child)

	def fill_list(self,data):
		if isinstance(data, collections.abc.MutableMapping):
			self.lst.DeleteAllItems()
			for k,v in data.items():
				self.lst.Append((k, *self.format_value(v)))
		elif isinstance(data, list):
			self.lst.DeleteAllItems()
			for i in range(len(data)):
				self.lst.Append(('[{}]'.format(i), *self.format_value(data[i])))
		elif isinstance(data, (str,int,bool)) or data == None:
			data = self.tree.GetItemData(self.tree.GetItemParent(self.node))
			self.fill_list(data)

	def format_value(self, value):
		if isinstance(value, list):
			return '[{}]'.format(len(value)),"node"
		elif isinstance(value, dict):
			return '{' + ','.join(value.keys()) + '}',"list"
		elif value == None:
			return "null","null"
		else:
			return value,type(value).__name__
