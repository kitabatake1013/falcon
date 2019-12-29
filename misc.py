﻿# -*- coding: utf-8 -*-
#Falcon miscellaneous helper objects
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Note: All comments except these top lines will be written in Japanese. 

import ctypes
import os
import time
import win32api
import win32file

falconHelper=ctypes.cdll.LoadLibrary("falconHelper.dll")

class Timer:
	"""シンプルなタイマー。経過時間や処理時間を計測するのに使う。単位は秒で、float。"""
	def __init__(self):
		self.started=time.time()

	@property
	def elapsed(self):
		return time.time()-self.started

#ヘルパー関数群

UNIT_AUTO=-1
UNIT_B=0
UNIT_KB=1
UNIT_MB=2
UNIT_GB=3
UNIT_TB=4
UNIT_STR=("Bytes", "KB", "MB", "GB", "TB")

def ConvertBytesTo(b, unit, appendUnit=False):
	"""バイト数を受け取って、指定された単位を使ったサイズを返す。appendUnit=True にすると、単位の文字列を最後に付けてくれる。"""
	if b<0:return ""
	num=0
	if unit==UNIT_AUTO: unit=DetermineSizeUnit(b)
	if unit==UNIT_B:
		num=b
	elif unit==UNIT_KB:
		num=b/1024
	elif unit==UNIT_MB:
		num=b/1024/1024
	elif unit==UNIT_GB:
		num=b/1024/1024/1024
	if unit==UNIT_TB:
		num=b/1024/1024/1024/1024
	#end 単位
	if not unit==UNIT_B:
		ret="%.2f" % num
	else:
		ret=""+str(num)
	if appendUnit: ret+=UNIT_STR[unit]
	return ret

def DetermineSizeUnit(b):
	"""バイト数を受け取って、それをサイズ単位に変換する際に最適な単位を、UNIT_* 定数で返す。"""
	global UNIT_B, UNIT_KB, UNIT_MB, UNIT_GB
	m=1024;
	if b<m: return UNIT_B
	m*=1024
	if b<m: return UNIT_KB
	m*=1024
	if b<m: return UNIT_MB
	m*=1024;
	if b<m: return UNIT_GB;
	return UNIT_TB;

def PTime2string(ptime):
	"""ptime 形式のオブジェクトを受け取って、人間が読めるタイムスタンプ文字列に変換して返す。"""
	return "%04d/%02d/%02d %02d:%02d:%02d" % (ptime.year, ptime.month, ptime.day, ptime.hour, ptime.minute, ptime.second)

#ptimeをwx.DateTimeに変換する
def PTimeToDateTime(pTime):
	return wx.DateTime(pTime.day,pTime.month,pTime.year,pTime.hour,pTime.minute,pTime.second,pTime.msec)

def attrib2dward(readonly=False, hidden=False, system=False, archive=False):
	ret=0
	if readonly is True: ret=ret|win32file.FILE_ATTRIBUTE_READONLY
	if hidden is True: ret=ret|win32file.FILE_ATTRIBUTE_HIDDEN
	if system is True: ret=ret|win32file.FILE_ATTRIBUTE_SYSTEM
	if archive is True: ret=ret|win32file.FILE_ATTRIBUTE_ARCHIVE
	if ret==0: ret=win32file.FILE_ATTRIBUTE_NORMAL
	return ret

def getDiscDriveTypes():
	ptr=falconHelper.getDiscDriveTypes()
	s=ctypes.c_char_p(ptr).value
	falconHelper.releasePtr(ptr)
	s2=s.decode('utf-8').split("\n")
	ret={}
	for elem in s2:
		if elem=="": continue
		tmp=elem.split(",")
		ret[tmp[0].rstrip(":\\")]=(tmp[1],tmp[2])
	#end for
	return ret
#end getDiscDriveTypes

def disableWindowStyleFlag(hwnd,flag):
	"""指定されたウィンドウハンドルの DWL_STYLE の値を撮って、指定されたフラグを折る。"""
	value=win32api.GetWindowLong(hwnd,-16)#-16 が DWL_STYLE らしい
	tmp=0xffffffff-flag
	value=value&tmp
	win32api.SetWindowLong(hwnd,-16,value)

def IteratePaths(path):
	"""FindFirstFile 系を使う"""
	for elem in win32file.FindFilesIterator(path+"\\*"):
		if elem[8]=="." or elem[8]=="..": continue
		if elem[0]&win32file.FILE_ATTRIBUTE_DIRECTORY: 
			yield from IteratePaths2(os.path.join(path,elem[8]))
		#end ディレクトリ
		yield os.path.join(path,elem[8])

def GetDirectorySize(path):
	"""ディレクトリのサイズをバイト数で返す。"""
	total = 0
	with os.scandir(path) as it:
		for entry in it:
			if entry.is_file():
				total += entry.stat().st_size
			elif entry.is_dir():
				total+=GetDirectorySize(entry.path)
	return total
