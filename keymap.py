﻿# -*- coding: utf-8 -*-
#Falcon key map management
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import configparser
import logging
import os
import wx
import defaultKeymap
import errorCodes
import menuItemsStore

import tabs
import browsableObjects

from simpleDialog import *

str2ControlCommand={
	#制御キー
	"CONTROL_A":wx.WXK_CONTROL_A,
	"CONTROL_B":wx.WXK_CONTROL_B,
	"CONTROL_C":wx.WXK_CONTROL_C,
	"CONTROL_D":wx.WXK_CONTROL_D,
	"CONTROL_E":wx.WXK_CONTROL_E,
	"CONTROL_F":wx.WXK_CONTROL_F,
	"CONTROL_G":wx.WXK_CONTROL_G,
	"CONTROL_H":wx.WXK_CONTROL_H,
	"CONTROL_I":wx.WXK_CONTROL_I,
	"CONTROL_J":wx.WXK_CONTROL_J,
	"CONTROL_K":wx.WXK_CONTROL_K,
	"CONTROL_L":wx.WXK_CONTROL_L,
	"CONTROL_M":wx.WXK_CONTROL_M,
	"CONTROL_N":wx.WXK_CONTROL_N,
	"CONTROL_O":wx.WXK_CONTROL_O,
	"CONTROL_P":wx.WXK_CONTROL_P,
	"CONTROL_Q":wx.WXK_CONTROL_Q,
	"CONTROL_R":wx.WXK_CONTROL_R,
	"CONTROL_S":wx.WXK_CONTROL_S,
	"CONTROL_T":wx.WXK_CONTROL_T,
	"CONTROL_U":wx.WXK_CONTROL_U,
	"CONTROL_V":wx.WXK_CONTROL_V,
	"CONTROL_W":wx.WXK_CONTROL_W,
	"CONTROL_X":wx.WXK_CONTROL_X,
	"CONTROL_Y":wx.WXK_CONTROL_Y,
	"CONTROL_Z":wx.WXK_CONTROL_Z
}

#マウスボタン
str2MouseKey={
	"LBUTTON":wx.WXK_LBUTTON,
	"MBUTTON":wx.WXK_MBUTTON,
	"RBUTTON":wx.WXK_RBUTTON
}

#他の全てのキーの修飾キーとして利用可能
str2ModifierKey={
	#修飾キー
	"ALT":wx.WXK_ALT,
	"CTRL":wx.WXK_CONTROL,
	"WINDOWS":wx.WXK_WINDOWS_LEFT,
	"WINDOWS_RIGHT":wx.WXK_WINDOWS_RIGHT,
	"SHIFT":wx.WXK_SHIFT
}

#不明なもの・Windowsでは使えないもの、
str2UnknownKey={
	"START":wx.WXK_START,					#Ctrl+ESC
	"CANCEL":wx.WXK_CANCEL,
	"MENU":wx.WXK_MENU,
	"CAPITAL":wx.WXK_CAPITAL,
	"SELECT":wx.WXK_SELECT,
	"PRINT":wx.WXK_PRINT,
	"EXECUTE":wx.WXK_EXECUTE,
	"HELP":wx.WXK_HELP,
	"SCROLL":wx.WXK_SCROLL,					#ScrLk
	"COMMAND":wx.WXK_COMMAND,				#CONTROLと同じ
	"RAW_CONTROL":wx.WXK_RAW_CONTROL,		#CONTROLと同じ
	"CLEAR":wx.WXK_CLEAR,					#テンキー5

	#記号キー 動作しない
	"MULTIPLY":wx.WXK_MULTIPLY,
	"ADD":wx.WXK_ADD,
	"SEPARATOR":wx.WXK_SEPARATOR,
	"SUBTRACT":wx.WXK_SUBTRACT,
	"DECIMAL":wx.WXK_DECIMAL,
	"DIVIDE":wx.WXK_DIVIDE,
}

#単独でも修飾キーとの組み合わせでも利用可能
str2FunctionKey={
	#ファンクションキー
	"F1":wx.WXK_F1,
	"F2":wx.WXK_F2,
	"F3":wx.WXK_F3,
	"F4":wx.WXK_F4,
	"F5":wx.WXK_F5,
	"F6":wx.WXK_F6,
	"F7":wx.WXK_F7,
	"F8":wx.WXK_F8,
	"F9":wx.WXK_F9,
	"F10":wx.WXK_F10,
	"F11":wx.WXK_F11,
	"F12":wx.WXK_F12,
	"F13":wx.WXK_F13,
	"F14":wx.WXK_F14,
	"F15":wx.WXK_F15,
	"F16":wx.WXK_F16,
	"F17":wx.WXK_F17,
	"F18":wx.WXK_F18,
	"F19":wx.WXK_F19,
	"F20":wx.WXK_F20,
	"F21":wx.WXK_F21,
	"F22":wx.WXK_F22,
	"F23":wx.WXK_F23,
	"F24":wx.WXK_F24,
}

#文字入力時に利用できない単独キー
str2InputControlKey={
	"BACK":wx.WXK_BACK,
	"SPACE":wx.WXK_SPACE,
	"DELETE":wx.WXK_DELETE,
	"INSERT":wx.WXK_INSERT,

	#ジャンプキー
	"HOME":wx.WXK_HOME,
	"END":wx.WXK_END,
	"PAGEUP":wx.WXK_PAGEUP,
	"PAGEDOWN":wx.WXK_PAGEDOWN,
}

#主要キー
str2StandaloneKey={
	"TAB":wx.WXK_TAB,
	"RETURN":wx.WXK_RETURN,
	"ESCAPE":wx.WXK_ESCAPE,
	"APPLICATIONS":wx.WXK_WINDOWS_MENU,		#コンテキストメニューを開くアプリケーションキー
	"PRINTSCREEN":wx.WXK_SNAPSHOT,		#PrintScr
	"PAUSE":wx.WXK_PAUSE,

	#テンキー記号キー
	"NUMPAD_EQUAL":wx.WXK_NUMPAD_EQUAL,
	"NUMPAD_MULTIPLY":wx.WXK_NUMPAD_MULTIPLY,
	"NUMPAD_ADD":wx.WXK_NUMPAD_ADD,
	"NUMPAD_SEPARATOR":wx.WXK_NUMPAD_SEPARATOR,
	"NUMPAD_SUBTRACT":wx.WXK_NUMPAD_SUBTRACT,
	"NUMPAD_DIVIDE":wx.WXK_NUMPAD_DIVIDE,
	"NUMPAD_DECIMAL":wx.WXK_NUMPAD_DECIMAL,

	#矢印キー
	"LEFTARROW":wx.WXK_LEFT,
	"UPARROW":wx.WXK_UP,
	"RIGHTARROW":wx.WXK_RIGHT,
	"DOWNARROW":wx.WXK_DOWN,
}

#単独または修飾キーとの組み合わせで利用できる
str2SpecialKey={
	#メディア制御キー
	"VOLUME_DOWN":wx.WXK_VOLUME_DOWN,
	"VOLUME_MUTE":wx.WXK_VOLUME_MUTE,
	"VOLUME_UP":wx.WXK_VOLUME_UP,
	"MEDIA_NEXT":wx.WXK_MEDIA_NEXT_TRACK,
	"MEDIA_PLAY":wx.WXK_MEDIA_PLAY_PAUSE,
	"MEDIA_BACK":wx.WXK_MEDIA_PREV_TRACK,
	"MEDIA_STOP":wx.WXK_MEDIA_STOP,

	#ブラウザ制御キー
	"BROWSER_BACK":wx.WXK_BROWSER_BACK,
	"BROWSER_FAVORITES":wx.WXK_BROWSER_FAVORITES,
	"BROWSER_FORWARD":wx.WXK_BROWSER_FORWARD,
	"BROWSER_HOME":wx.WXK_BROWSER_HOME,
	"BROWSER_REFRESH":wx.WXK_BROWSER_REFRESH,
	"BROWSER_SEARCH":wx.WXK_BROWSER_SEARCH,
	"BROWSER_STOP":wx.WXK_BROWSER_STOP,

	#アプリケーション起動キー
	"LAUNCH_APP1":wx.WXK_LAUNCH_APP1,
	"LAUNCH_APP2":wx.WXK_LAUNCH_APP2,
	"LAUNCH_MAIL":wx.WXK_LAUNCH_MAIL,

	#スペシャル
	"SPECIAL1":wx.WXK_SPECIAL1,
	"SPECIAL2":wx.WXK_SPECIAL2,
	"SPECIAL3":wx.WXK_SPECIAL3,
	"SPECIAL4":wx.WXK_SPECIAL4,
	"SPECIAL5":wx.WXK_SPECIAL5,
	"SPECIAL6":wx.WXK_SPECIAL6,
	"SPECIAL7":wx.WXK_SPECIAL7,
	"SPECIAL8":wx.WXK_SPECIAL8,
	"SPECIAL9":wx.WXK_SPECIAL9,
	"SPECIAL10":wx.WXK_SPECIAL10,
	"SPECIAL11":wx.WXK_SPECIAL11,
	"SPECIAL12":wx.WXK_SPECIAL12,
	"SPECIAL13":wx.WXK_SPECIAL13,
	"SPECIAL14":wx.WXK_SPECIAL14,
	"SPECIAL15":wx.WXK_SPECIAL15,
	"SPECIAL16":wx.WXK_SPECIAL16,
	"SPECIAL17":wx.WXK_SPECIAL17,
	"SPECIAL18":wx.WXK_SPECIAL18,
	"SPECIAL19":wx.WXK_SPECIAL19,
	"SPECIAL20":wx.WXK_SPECIAL20,
}

#他の修飾キーとの組み合わせで利用できるキー
str2CharactorKey={
	#アルファベットキー
	"A": ord('A'),
	"B": ord('B'),
	"C": ord('C'),
	"D": ord('D'),
	"E": ord('E'),
	"F": ord('F'),
	"G": ord('G'),
	"H": ord('H'),
	"I": ord('I'),
	"J": ord('J'),
	"K": ord('K'),
	"L": ord('L'),
	"M": ord('M'),
	"N": ord('N'),
	"O": ord('O'),
	"P": ord('P'),
	"Q": ord('Q'),
	"R": ord('R'),
	"S": ord('S'),
	"T": ord('T'),
	"U": ord('U'),
	"V": ord('V'),
	"W": ord('W'),
	"X": ord('X'),
	"Y": ord('Y'),
	"Z": ord('Z'),

	#数字キー
	"0": ord('0'),
	"1": ord('1'),
	"2": ord('2'),
	"3": ord('3'),
	"4": ord('4'),
	"5": ord('5'),
	"6": ord('6'),
	"7": ord('7'),
	"8": ord('8'),
	"9": ord('9'),

	#テンキー数字キー
	"NUMPAD0":wx.WXK_NUMPAD0,
	"NUMPAD1":wx.WXK_NUMPAD1,
	"NUMPAD2":wx.WXK_NUMPAD2,
	"NUMPAD3":wx.WXK_NUMPAD3,
	"NUMPAD4":wx.WXK_NUMPAD4,
	"NUMPAD5":wx.WXK_NUMPAD5,
	"NUMPAD6":wx.WXK_NUMPAD6,
	"NUMPAD7":wx.WXK_NUMPAD7,
	"NUMPAD8":wx.WXK_NUMPAD8,
	"NUMPAD9":wx.WXK_NUMPAD9,

	#記号キー
	",": ord(','),
	".": ord('.'),
	"/": ord('/'),
	"\\": ord('\\'),	#上段側のみにマッチ
	";": ord(';'),
	":": ord(':'),
	"[": ord('['),
	"]": ord(']'),
	"@": ord('@'),
	"-": ord('-'),
	"^": ord('^'),
}

#利用不可
str2categoryKey={
	#カテゴリ制御キー
	"CATEGORY_ARROW":wx.WXK_CATEGORY_ARROW,
	"CATEGORY_CUT":wx.WXK_CATEGORY_CUT,
	"CATEGORY_JUMP":wx.WXK_CATEGORY_JUMP,
	"CATEGORY_NAVIGATION":wx.WXK_CATEGORY_NAVIGATION,
	"CATEGORY_PAGING":wx.WXK_CATEGORY_PAGING,
	"CATEGORY_TAB":wx.WXK_CATEGORY_TAB,
}

#テンキー関連の内、本来のキーと重複して判定されてしまうキー
str2numpadKey={
	"NUMPAD_F1":wx.WXK_NUMPAD_F1,
	"NUMPAD_F2":wx.WXK_NUMPAD_F2,
	"NUMPAD_F3":wx.WXK_NUMPAD_F3,
	"NUMPAD_F4":wx.WXK_NUMPAD_F4,

	"NUMPAD_SPACE":wx.WXK_NUMPAD_SPACE,
	"NUMPAD_INSERT":wx.WXK_NUMPAD_INSERT,
	"NUMPAD_DELETE":wx.WXK_NUMPAD_DELETE,

	"NUMPAD_LEFT":wx.WXK_NUMPAD_LEFT,	#4
	"NUMPAD_UP":wx.WXK_NUMPAD_UP,		#8
	"NUMPAD_RIGHT":wx.WXK_NUMPAD_RIGHT,	#6
	"NUMPAD_DOWN":wx.WXK_NUMPAD_DOWN,	#2

	"NUMPAD_PAGEUP":wx.WXK_NUMPAD_PAGEUP,#9
	"NUMPAD_PAGEDOWN":wx.WXK_NUMPAD_PAGEDOWN,#3
	"NUMPAD_HOME":wx.WXK_NUMPAD_HOME,	#7
	"NUMPAD_END":wx.WXK_NUMPAD_END,		#9

	"NUMPAD_TAB":wx.WXK_NUMPAD_TAB,
	"NUMPAD_ENTER":wx.WXK_NUMPAD_ENTER,
}

str2key={}
str2key.update(**str2ControlCommand,**str2MouseKey,**str2ModifierKey,**str2UnknownKey,**str2FunctionKey,**str2InputControlKey,**str2StandaloneKey,**str2SpecialKey,**str2CharactorKey,**str2categoryKey,**str2numpadKey)

class KeymapHandler():
	"""wxのアクセラレーターテーブルを生成します。"""

	def __init__(self,dict=None,filter=None):
		#wx.AcceleratorEntry.__eq__=AcceleratorEntry_eq
		self.log=logging.getLogger("falcon.keymapHandler")
		self.errors={}
		self.entries={}		#生成したAcceleratorEntry
		self.map={}			#ref番号→ショートカットキーに変換
		self.refMap={}		#キーの重複によりこのインスタンスで処理する必要のあるメニューと、そのとび先の本来のref
		self.filter=filter	#指定の妥当性をチェックするフィルタ

		if dict:
			self.addDict(dict)

	def addDict(self,dict):
		read=configparser.ConfigParser()
		read.read_dict(dict)
		for identifier in read.sections():
			for elem in read.items(identifier):
				if elem[1]!="":						#空白のものは無視する
					self.add(identifier,elem[0],elem[1])

	def addFile(self, filename):
		"""
			指定されたファイルを読もうと試みます。ファイルが見つからなかった場合は、FILE_NOT_FOUND を返します。ファイルがパースできなかった場合は、PARSING_FAILED を返します。
			errorCodes.OKが返された場合であっても、キーの重複などで追加できなかったものがあった可能性があります。これについては、その情報がself.errorsに格納されるので呼出元で検証する必要があります。
		"""
		if not os.path.exists(filename):
			self.log.warning("Cannot find %s" % filename)
			return errorCodes.FILE_NOT_FOUND
		newKeys=configparser.ConfigParser()
		ret=newKeys.read(filename, encoding="UTF-8")
		ret= errorCodes.OK if len(ret)>0 else errorCodes.PARSING_FAILED
		if ret==errorCodes.PARSING_FAILED:
			self.log.warning("Cannot parse %s" % filename)
			return ret

		#newKeysの情報を、検証しながらaddしていく
		for identifier in newKeys.sections():
			for elem in newKeys.items(identifier):
				if elem[1]!="":				#空白のものは無視する
					self.add(identifier,elem[0],elem[1])
		return errorCodes.OK

	def GetError(self,identifier):
		"""指定されたビューのエラー内容を返し、内容をクリアする"""
		identifier=identifier.upper()
		try:
			ret=self.errors[identifier]
		except KeyError:
			return {}
		self.errors[identifier]={}
		return ret

	def add(self,identifier,ref,key):
		"""重複をチェックしながらキーマップにショートカットを追加します。"""
		#refとidentifierは大文字・小文字の区別をしないので大文字に統一
		ref=ref.upper()
		identifier=identifier.upper()

		#identifierが新規だった場合、self.mapとself.entriesにセクション作成
		if not identifier in self.map.keys():
			self.entries[identifier]=[]
			self.map[identifier]={}

		#エントリーの作成・追加
		for e in key.split("/"):
			entry=makeEntry(ref,e,self.filter,self.log)
			if entry==False:
				self.addError(identifier,ref,key)
				continue

			#キーの重複確認
			checkList=[]		#要確認リスト
			for i in self.entries[identifier]:
				if entry==i:
					checkList.append(i)
			if checkList:
					checkList.append(entry)
					if self.checkConfrict(checkList,identifier):
						entry=None
					else:
						self.addError(identifier,ref,key)
						continue

			#GetKeyStringに備えてself.mapに追加
			if ref in self.map[identifier]:
				#refが重複の場合、既存のself.map上のエントリの末尾に追加
				self.map[identifier][ref]=self.map[identifier][ref]+"/"+e
			else:
				#self.mapに新規エントリとして追加
				self.map[identifier][ref]=e

			#self.entriesに追加
			#重複確認・置換処理の関係でNoneになってる場合には既に追加済みを意味するのでここでは何もしない
			if entry:
				self.entries[identifier].append(entry)
		return

	def addError(self,identifier,ref,key):
		"""エラー発生時、情報を記録します。"""
		try:
			self.errors[identifier][ref]=key
		except KeyError:
			self.errors[identifier]={}
			self.errors[identifier][ref]=key

	def GetKeyString(self,identifier,ref):
		"""指定されたコマンドのショートカットキー文字列を取得します。"""
		ref=ref.upper()
		identifier=identifier.upper()

		try:
			r=self.map[identifier][ref]
		except KeyError:
			r=None
		#end except
		return r

	def GetTable(self, identifier):
		"""アクセラレーターテーブルを取得します。identifier で、どのビューでのテーブルを取得するかを指定します。"""
		identifier=identifier.upper()
		return wx.AcceleratorTable(self.entries[identifier])

	def GetEntries(self,identifier):
		"""登録されているエントリーの一覧を取得します。identifier で、どのビューでのテーブルを取得するかを指定します。"""
		identifier=identifier.upper()
		return self.entries[identifier]

	#複数メニューに対するキーの割り当ての重複を許すか否かを調べる
	#itemsには調べたいAcceleratorEntryのリストを入れる
	def checkConfrict(self,items,identifier):
		flg=0
		for i in [j.refName for j in items]:
			iFlag=0
			if i not in tabs.base.FalconTabBase.selectItemTypeMenuConditions[browsableObjects.File]:
					iFlag+=1
			if i not in tabs.base.FalconTabBase.selectItemTypeMenuConditions[browsableObjects.Folder]:
				iFlag+=2
			if i not in tabs.streamList.StreamListTab.blockMenuList:
				iFlag+=4
			if i not in tabs.driveList.DriveListTab.blockMenuList:
				iFlag+=8
			#print(i+":"+str(iFlag))
			if iFlag&flg==0:
				flg+=iFlag
			else:
				#重複によるエラー
				self.log.warn("key confricted. "+i+" is confrict in "+str(items))
				return False
		self.log.debug("key not confricted. "+i+" is not confrict in "+str(items))

		#重複してるが問題なしの場合
		#refを書き換える
		newref=menuItemsStore.getRef("keymap_"+items[0].ToRawString())
		self.refMap[newref]=[]

		#self.entriesからいったん削除
		for i in range(len(items)-1):
			self.entries[identifier].remove(items[0])

		#refを差し替えて再登録
		for i in items:
			self.refMap[newref].append(i.GetCommand())
			self.entries[identifier].append(AcceleratorEntry(i.GetFlags(),i.GetKeyCode(),newref,i.GetRefName()))
		return True

	def isRefHit(self,ref):
		return ref in self.refMap

	def GetOriginalRefs(self,ref):
		return self.refMap[ref]

def makeEntry(ref,key,filter,log):
	"""ref(String)と、/区切りでない単一のkey(String)からwx.AcceleratorEntryを生成"""
	key=key.upper()					#大文字に統一して処理

	#修飾キーの確認
	ctrl="CTRL+" in key
	alt="ALT+" in key
	shift="SHIFT+" in key
	codestr=key.split("+")
	flags=0
	flagCount=0
	if ctrl:
		flags=wx.ACCEL_CTRL
		flagCount+=1
	if alt:
		flags=flags|wx.ACCEL_ALT
		flagCount+=1
	if shift:
		flags=flags|wx.ACCEL_SHIFT
		flagCount+=1

	#修飾キーのみのもの、修飾キーでないキーが複数含まれるものはダメ
	if not len(codestr)-flagCount==1:
		return False

	codestr=codestr[len(codestr)-1]
	if not codestr in str2key:			#存在しないキーの指定はエラー
		return False

	#フィルタの確認
	if filter and not filter.Check(key):
		log.warning("%s(%s): %s" % (ref,key,filter.GetLastError()))
		print("%s(%s): %s" % (ref,key,filter.GetLastError()))

		return False
	return AcceleratorEntry(flags,str2key[codestr],menuItemsStore.getRef(ref.upper()),ref.upper())



class AcceleratorEntry(wx.AcceleratorEntry):
	#ショートカットキーの一致によって判定され、登録されたメニューコマンドの一致は無視される
	#refをstrで保持する

	def __init__(self,flags,key,cmd,refName=""):
		super().__init__(flags,key,cmd)
		self.refName=refName

	def __eq__(self,other):
		# isinstance(other, Person)を除去
		if other is None or type(self) != type(other): return False
		if self.GetFlags()==other.GetFlags() and self.GetKeyCode()==other.GetKeyCode():
			return True
		return False

	def GetRefName(self):
		return self.refName

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return "<AcceleratorEntry %s>" % self.GetRefName()

class KeyFilter:
	"""
		利用できるショートカットキーを制限するためのフィルタ
	"""

	def __init__(self):
		"""
			必用な変数を作成し、OSが利用するコマンドとの重複は設定できないようブロックします。
		"""
		self.errorString=""									#最後に検知したエラーの原因を格納
		self.modifierKey=set()								#有効な修飾キー
		self.functionKey=set()								#有効なファンクションキー。単独または修飾キーとの組み合わせで利用可能
		self.enableKey=set()								#修飾キーとの組み合わせで利用可能
		self.noShiftEnableKey=set()							#SHIFTキー以外の修飾キーとの組み合わせで利用可能(modifierKeyにSHIFTを指定していない場合は無視される)
		self.disablePattern=[]								#無効なキーの組み合わせ
		self.AddDisablePattern("CTRL+ESCAPE")				#スタートメニュー
		self.AddDisablePattern("CTRL+SHIFT+ESCAPE")			#タスクマネージャ
		self.AddDisablePattern("CTRL+WINDOWS+RETURN")#ナレーターの起動と終了
		self.AddDisablePattern("ALT+SHIFT+PRINTSCREEN")		#ハイコントラストの切り替え
		self.AddDisablePattern("ALT+ESCAPE")				#最前面ウィンドウの最小化
		self.AddDisablePattern("ALT+TAB")					#ウィンドウの切り替え
		self.AddDisablePattern("ALT+SHIFT+TAB")				#ウィンドウの切り替え
		self.AddDisablePattern("PRINTSCREEN")				#スクリーンショットの取得
		self.AddDisablePattern("ALT+PRINTSCREEN")			#単一画面のスクリーンショット取得


	def SetDefault(self,supportInputChar,isSystem):
		"""
			フィルタを一般的な設定に構成します。
			supportInputCharには、そのウィンドウでの文字入力の可否を設定します。

			isSystemには、システム内部で設定する場合にはTrue、ユーザが独自で設定する場合にはFalseを指定します。
			ユーザが独自にキーをカスタマイズする場合に、指定することが望ましくないキーの組み合わせをブロックします。
			将来、開発者が機能拡張する際の問題を和らげることを目的としています。
			なお、開発者であってもコメントで記した目的以外に利用することは避けるべきです。
		"""
		self.modifierKey.add("CTRL")
		self.modifierKey.add("ALT")
		self.modifierKey.add("SHIFT")

		self.functionKey|=str2FunctionKey.keys()
		self.functionKey|=str2SpecialKey.keys()
		self.noShiftEnableKey|=str2CharactorKey.keys()

		if supportInputChar:
			#文字入力に関わる共通のショートカットは設定不可
			self.AddDisablePattern("CTRL+INSERT")		#コピー
			self.AddDisablePattern("SHIFT+INSERT")			#貼り付け
			self.AddDisablePattern("CTRL+Z")			#元に戻す
			self.AddDisablePattern("CTRL+X")			#切り取り
			self.AddDisablePattern("CTRL+C")			#コピー
			self.AddDisablePattern("CTRL+V")			#貼り付け
			self.AddDisablePattern("CTRL+A")			#すべて選択
			self.AddDisablePattern("CTRL+Y")			#やり直し
			self.AddDisablePattern("CTRL+F7")			#単語登録(日本語変換時のみ)
			self.AddDisablePattern("CTRL+F10")			#IMEメニュー表示(日本語変換時のみ)

			#単独で文字入力の制御に利用されるので修飾キー必須
			self.enableKey|=str2InputControlKey.keys()
		else:
			#単独で文字入力の制御に利用されるが、それがないなら単独利用可能
			self.functionKey|=str2InputControlKey.keys()

		if isSystem:
			self.functionKey|=str2StandaloneKey.keys()
		else:
			self.AddDisablePattern("APPLICATIONS")		#コンテキストメニューの表示
			self.AddDisablePattern("SHIFT+F10")			#コンテキストメニューの表示
			self.AddDisablePattern("F10")				#ALTキーの代わり
			self.AddDisablePattern("ESCAPE")			#操作の取り消し
			self.AddDisablePattern("ALT+F4")			#アプリケーションの終了
			self.AddDisablePattern("ALT+SPACE")			#リストビュー等で全ての選択を解除
			self.AddDisablePattern("TAB")				#カーソル移動
			self.AddDisablePattern("SHIFT+TAB")			#カーソル移動
			self.AddDisablePattern("UPARROW")			#カーソル移動
			self.AddDisablePattern("DOWNARROW")			#カーソル移動
			self.AddDisablePattern("RIGHTARROW")		#カーソル移動
			self.AddDisablePattern("LEFTARROW")			#カーソル移動
			self.AddDisablePattern("CTRL+TAB")			#ページ切り替え

			self.AddDisablePattern("CTRL+SHIFT+TAB")	#ページ切り替え

			self.enableKey|=str2StandaloneKey.keys()

		return self

	def AddDisablePattern(self,patternString):
		patterns=patternString.split("+")
		for ptn in patterns:
			ptn=ptn.upper()
			if not ptn in str2key:
				raise ValueError(_("%s は存在しないキーです。" % (ptn)))
		self.disablePattern.append(set(patterns))

	def AddEnableKey(self,keys):
		if type(keys)==str:
			return self.SetKeyGroup(keys,self.enableKey)
		for key in keys:
			self._SetKeyGroup(key,self.enableKey)

	def AddFunctionKey(self,keys):
		if type(keys)==str:
			return self.SetKeyGroup(keys,self.functionKey)
		for key in keys:
			self._SetKeyGroup(key,self.functionKey)

	def AddModifierKey(self,keys):
		if type(keys)==str:
			return self.SetKeyGroup(keys,self.modifierKey)
		for key in keys:
			self._SetKeyGroup(key,self.modifierKey)

	def AddNoShiftEnableKey(self,keys):
		if type(keys)==str:
			return self.SetKeyGroup(keys,noShiftEnableKey)
		for key in keys:
			self._SetKeyGroup(key,self.noShiftEnableKey)

	def _SetKeyGroup(self,key,target):
		key=key.upper()
		if not key in str2key:
			raise ValueError(_("%s は存在しないキーです。" % key))
		try:
			self.disablePattern.remove(set(key))
		except ValueError:
			pass
		self.enableKey.discard(key)
		self.functionKey.discard(key)
		self.modifierKey.discard(key)
		self.noShiftEnableKey.discard(key)
		target.add(key)


	def Check(self,keyString):
		if keyString=="":
			self.errorString="キーが指定されていません。"
			return False

		self.errorString=""
		keys=keyString.split("+")
		modFlg=False
		shiftFlg=False
		funcCount=0
		enableCount=0
		noShiftCount=0
		for key in keys:
			if key in self.modifierKey:
				if key=="SHIFT":
					shiftFlg=True
				else:
					modFlg=True
				continue
			if key in self.functionKey:
				funcCount+=1
				continue
			if key in self.enableKey:
				enableCount+=1
				continue
			if key in self.noShiftEnableKey:
				noShiftCount+=1
				continue

			#ここまでcontinue去れなかったらエラー
			self.errorString=_("%s は使用できないキーです。") % (key)
			return False

		#組み合わせの妥当性確認
		if len(keys)==1:
			if funcCount>0:
				return True
			else:
				if modFlg>0 or shiftFlg>0:
					self.errorString=_("修飾キーのみのパターンは設定できません。")
				else:
					self.errorString=_("このキーは修飾キーと合わせて指定する必要があります。")
				return False

		#２つ以上が指定されている場合
		if funcCount+enableCount+noShiftCount>1:
			self.errorString=_("非修飾キーの複数指定はできません。")
			return False
		elif modFlg==False and shiftFlg==False and funcCount==0:
			self.errorString=_("SHIFT以外の修飾キーと合わせて指定する必要があります。")
			return
		elif funcCount==0 and noShiftCount==0 and enableCount==0:
			self.errorString=_("修飾キーのみの組み合わせは指定できません。")
			return False
		if enableCount>0 and modFlg==False and shiftFlg==False:
			raise Error("コードのバグです。")
		if noShiftCount>0 and modFlg==False:
			self.errorString=_("SHIFT以外の修飾キーと合わせて指定する必要があります。")
			return False

		if set(keys) in self.disablePattern:
			self.errorString=_("この組み合わせは利用できません。")
			return False

		return True

	def GetLastError(self):
		return self.errorString

	def GetUsableKeys(self):
		ret=[]
		ret.extend([*self.modifierKey,*self.functionKey,*self.enableKey,*self.noShiftEnableKey])
		return ret
