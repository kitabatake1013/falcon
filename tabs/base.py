﻿# -*- coding: utf-8 -*-
#Falcon tab base object
#Copyright (C) 2019-2020 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

"""
タブは、必ずリストビューです。カラムの数と名前と、それに対応するリストの要素がタブを構成します。たとえば、ファイル一覧では「ファイル名」や「サイズ」などがカラムになり、その情報がリストに格納されています。ファイル操作の状況を示すタブの場合は、「進行率」や「状態」などがカラムの名前として想定されています。リスト上でエンターを押すことで、アクションを実行できます。ファイルビューではファイルやフォルダを開き、ファイル操作では問い合わせに応答することができます。
"""
import logging
import os

import wx
import browsableObjects
import clipboardHelper
import errorCodes
import globalVars
import lists
import misc
from . import navigator

class FalconTabBase(object):
	"""全てのタブに共通する基本クラス。"""
	def __init__(self):
		self.task=None
		self.colums=[]#タブに表示されるカラムの一覧。外からは読み取りのみ。
		self.listObject=None#リストの中身を保持している listObjects のうちのどれかのオブジェクト・インスタンス
		self.type=None
		self.isRenaming=False
		globalVars.app.config.add_section(self.__class__.__name__)
		self.environment={}		#このタブ特有の環境変数
		self.markedPlace=None	#マークフォルダ

	def Initialize(self,parent,creator,existing_listctrl=None):
		"""タブを初期化する。親ウィンドウの上にリストビューを作るだけ。existing_listctrl にリストコントロールがある場合、そのリストコントロールを再利用する。"""
		self.log=logging.getLogger("falcon.%s" % self.__class__.__name__)
		self.log.debug("Created.")
		self.parent=parent
		self.InstallListCtrl(creator,existing_listctrl)
		self.background_tasks=[]

	def InstallListCtrl(self,creator,existing_listctrl=None):
		"""指定された親パネルの子供として、このタブ専用のリストコントロールを生成する。"""
		if existing_listctrl is None:
			self.hListCtrl=creator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_EDIT_LABELS)
			creator.GetPanel().Layout()
		else:
			self.hListCtrl=existing_listctrl
		#end リストコントロールを再利用する
		self.hListCtrl.Bind(wx.EVT_LIST_COL_CLICK,self.col_click)
		self.hListCtrl.Bind(wx.EVT_LIST_COL_END_DRAG,self.col_resize)
		self.hListCtrl.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT,self.OnLabelEditStart)
		self.hListCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT,self.OnLabelEditEnd)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.EnterItem)
		self.hListCtrl.Bind(wx.EVT_KEY_DOWN,self.KeyDown)
		self.hListCtrl.Bind(wx.EVT_LIST_BEGIN_DRAG,self.BeginDrag)

	def GetListColumns(self):
		return self.columns

	def GetItems(self):
		"""タブのリストの中身を取得する。"""
		return self.listObject.GetItems() if self.listObject is not None else []

	def GetFocusedItem(self):
		"""現在フォーカスが当たっているアイテムのインデックス番号を取得する。"""
		return self.hListCtrl.GetFocusedItem()

	def GetFocusedElement(self):
		"""現在フォーカスが当たっているアイテムをbrowsableObjectsで返す"""
		if self.GetFocusedItem()<0:
			return None
		return self.listObject.GetElement(self.GetFocusedItem())

	# 選択されているアイテムが１つ以上存在するか否か
	def IsItemSelected(self):
		return self.hListCtrl.GetSelectedItemCount()>0

	def GetSelectedItemCount(self):
		return self.hListCtrl.GetSelectedItemCount()

	def GetSelectedItems(self,index_mode=False):
		"""選択中のアイテムを、 ListObject で帰す。index_mode が true の場合、 リスト上での index のリストを返す。"""
		next=self.hListCtrl.GetFirstSelected()
		if next==-1: return None
		lst=[]
		while(True):
			if index_mode:
				lst.append(next)
			else:
				lst.append(self.listObject.GetElement(next))
			next=self.hListCtrl.GetNextSelected(next)
			if next==-1: break
		#end while
		#リストを作る
		if index_mode: return lst
		r=type(self.listObject)()
		r.Initialize(lst)
		return r
		#end GetSelectedItems

	def GetListCtrl(self):
		return self.hListCtrl

	def SetListColumns(self,lst):
		"""リストコントロールにカラムを設定する。"""
		col=lst.GetColumns()
		self.hListCtrl.DeleteAllColumns()
		i=0
		for elem,format in col.items():
			self.hListCtrl.InsertColumn(i,elem,format=format,width=wx.LIST_AUTOSIZE)
			i+=1
		#end カラムを作る
		#カラム幅を設定
		for i in range(0,len(col)):
			w=globalVars.app.config[lst.__class__.__name__]["column_width_"+str(i)]
			w=100 if w=="" else int(w)
			self.hListCtrl.SetColumnWidth(i,w)
		#end カラム幅を設定
#end SetListColumns

	def UpdateListContent(self,content):
		"""リストコントロールの中身を更新する。カラム設定は含まない。"""
		self.log.debug("Updating list control...")
		self._cancelBackgroundTasks()
		t=misc.Timer()
		for elem in content:
			self.hListCtrl.Append(elem)
		#end 追加
		self.log.debug("List control updated in %f seconds." % t.elapsed)

	def TriggerAction(self, action,admin=False):
		"""タブの指定要素に対してアクションを実行する。成功した場合は、errorCodes.OK を返し、失敗した場合は、その他のエラーコードを返す。admin=True で、管理者として実行する。"""
		return errorCodes.NOT_SUPPORTED#基底クラスではなにも許可しない

	def EnterItem(self,event):
		"""アイテムの上でエンターを押したときに実行される。本当はビューのショートカットキーにしたかったんだけど、エンターの入力だけはこっちでとらないとできなかった。"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def MarkSet():
		"""現在開いている場所をマークする"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def KeyDown(self,event):
		"""キーが押されたらここにくる。SpaceがEnterと同一視されるので対策する。"""
		if not event.GetKeyCode()==32:
			event.Skip()
		else:
			self.OnSpaceKey()

	def OnSpaceKey(self):
		"""Spaceキーが押されたらこれが呼ばれる。"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね


	def BeginDrag(self,event):
		"""ドラッグ操作が開始された"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def SelectAll(self):
		globalVars.app.say(_("全て選択"))
		for i in range(self.hListCtrl.GetItemCount()):
			self.hListCtrl.Select(i)

	def NameCopy(self):
		if not self.IsItemSelected(): return
		globalVars.app.say(_("ファイル名をコピー"))
		t=self.GetSelectedItems().GetItemNames()
		t="\n".join(t)
		with clipboardHelper.Clipboard() as c:
			c.set_unicode_text(t)

	def FullpathCopy(self):
		if not self.IsItemSelected(): return
		t=self.GetSelectedItems().GetItemPaths()
		globalVars.app.say(_("フルパスをコピー"))
		t="\n".join(t)
		with clipboardHelper.Clipboard() as c:
			c.set_unicode_text(t)

	def UpdateFilelist(self,silence=False,cursorTargetName=""):
		"""同じフォルダで、ファイルとフォルダ情報を最新に更新する。"""
		if silence==True:
			globalVars.app.say(_("更新"))
		if cursorTargetName=="":
			item=self.listObject.GetElement(self.GetFocusedItem())
		result=self.listObject.Update()
		if result != errorCodes.OK:
			return errorCodes.FILE_NOT_FOUND			#アクセス負荷など
		if cursorTargetName=="":
			cursor=self.listObject.Search(item.basename,0)
		else:
			cursor=self.listObject.Search(cursorTargetName,0)
		self.Update(self.listObject,cursor)

	def SortCycleAd(self):
		"""昇順と降順を交互に切り替える。"""
		self.listObject.SetSortDescending(self.listObject.GetSortDescending()==0)
		self._updateConfig()
		self.listObject.ApplySort()
		self.hListCtrl.DeleteAllItems()
		self.UpdateListContent(self.listObject.GetItems())

	def SortSelect(self):
		"""並び順を指定する。"""
		m=wx.Menu()
		s=self.listObject.GetSupportedSorts()
		i=0
		for elem in s:
			m.Append(i,lists.GetSortDescription(elem))
			i+=1
		#end 追加
		item=self.hListCtrl.GetPopupMenuSelectionFromUser(m)
		m.Destroy()
		self.listObject.SetSortCursor(item)
		self._updateConfig()
		self.listObject.ApplySort()
		self.hListCtrl.DeleteAllItems()
		self.UpdateListContent(self.listObject.GetItems())

	def _updateConfig(self):
		"""ソートの設定をconfigに反映する。"""
		s=self.listObject.__class__.__name__
		globalVars.app.config[s]["sorting"]=self.listObject.GetSortCursor()
		globalVars.app.config[s]["descending"]=int(self.listObject.GetSortDescending())

	def col_resize(self,event):
		no=event.GetColumn()
		width=self.hListCtrl.GetColumnWidth(no)
		globalVars.app.config[self.listObject.__class__.__name__]["column_width_"+str(no)]=str(width)

	def col_click(self,event):
		no=event.GetColumn()
		self.listObject.SetSortCursor(no)
		if self.listObject.GetSortCursor()==no:
			self.listObject.SetSortDescending(self.listObject.GetSortDescending()==0)
		self._updateConfig()
		self.listObject.ApplySort()
		self.hListCtrl.DeleteAllItems()
		self.UpdateListContent(self.listObject.GetItems())

	def SortNext(self):
		self.listObject.SetSortCursor()
		self._updateConfig()
		self.listObject.ApplySort()
		self.hListCtrl.DeleteAllItems()
		self.UpdateListContent(self.listObject.GetItems())
	#end sortNext

	def _cancelBackgroundTasks(self):
		"""フォルダ容量計算など、バックグラウンドで走っていて、ファイルリストが更新されるといらなくなるようなものをキャンセルする。"""
		for elem in self.background_tasks:
			elem.Cancel()
		#end for
		self.background_tasks=[]

	def EnterItem(self,event):
		"""forward アクションを実行する。"""
		globalVars.app.hMainView.events.GoForward()

	def Move(self,path,cursor=""):
		"""指定の場所へ移動する。"""
		r=navigator.Navigate(path,cursor,previous_tab=self)
		return errorCodes.OK if r is self else r

	def GoForward(self,stream,admin=False):
		"""選択中のフォルダに入るか、選択中のファイルを実行する。stream=True の場合、ファイルの NTFS 副ストリームを開く。"""
		index=self.GetFocusedItem()
		elem=self.listObject.GetElement(index)
		if isinstance(elem,browsableObjects.Folder):#このフォルダを開く
			#TODO: 管理者モードだったら、別のfalconが昇格して開くように
			return self.Move(elem.fullpath)
		#end フォルダ開く
		elif isinstance(elem,browsableObjects.File):#このファイルを開く
			if not stream:
				misc.RunFile(elem.fullpath,admin)
				return
			else:
				return self.Move(elem.fullpath)
		#end ファイルを開く
		#end なにを開くか
	#end GoForward

	def GoBackward(self):
		"""内包しているフォルダ/ドライブ一覧へ移動する。"""
		if len(self.listObject.rootDirectory)<=3:		#ドライブリストへ
			target=""
			cursorTarget=self.listObject.rootDirectory[0]
		else:
			target=os.path.split(self.listObject.rootDirectory)[0]
			cursorTarget=os.path.split(self.listObject.rootDirectory)[1]
		return self.Move(target,cursorTarget)
