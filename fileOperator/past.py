# -*- coding: utf-8 -*-
#Falcon file operation handler copy
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Note: All comments except these top lines will be written in Japanese. 
import logging
import os
import re
import win32file
import misc

from . import helper

VERB="past"
log=logging.getLogger("falcon.%s" % VERB)

class Element(object):
	"""コピー/移動する項目の情報を持っておく。"""
	def __init__(self,path,basepath,destpath):
		self.path=path
		self.destpath=path.replace(basepath,destpath)#これがコピー先
		self.isfile=os.path.isfile(path)
		self.size=os.path.getsize(path) if self.isfile else -1
	#end __init__
#end Element

def Execute(op):
	"""実行処理。リトライが必要になった項目数を返す。"""
	retry=0
	try:
		f=op.instructions["target"]
	except KeyError:
		log.error("Required key is not specified.")
		return False
	#end 処理刷るものなし
	op.output["all_OK"]=True
	op.output["retry"]["target"]=[]
	op.output["percentage"]=0
	#ベースパスを決定
	basepath=os.path.dirname(f[0])
	destpath=op.instructions['to']
	log.debug("Base path: %s dest path: %s" % (basepath,destpath))
	log.debug("Retrieving file list...")
	lst=[]
	for elem in f:
		if not basepath in elem:
			debug.log("Umpatched base path, skipping %s" % elem)
			continue
		#end ベースパスが合わない
		if os.path.isfile(elem):
			lst.append(Element(elem,basepath,destpath))
		else:
			lst.append(Element(elem,basepath,destpath))#イテレーションの最初に親フォルダ追加
			for elem2 in misc.IteratePaths_dirFirst(elem):
				lst.append(Element(elem2,basepath,destpath))
			#end フォルダからファイルリスト
		#end フォルダだった
	#end ファイルリスト作るループ
	#ファイルリスト作ったので、もともとの target に上書き
	f=lst
	log.debug("%d items found." % len(f))
	#コピーサイズの合計を計算
	total=0
	for elem in f:
		if elem.size!=-1: total+=elem.size
	#end サイズを足す
	op.output['total_bytes']=total
	op.output['current_bytes']=0
	log.debug("Size: %d bbytes" % total)
	log.debug("Start copying...")
	for elem in f:
		try:
			if os.path.isfile(elem):
				win32file.CopyFileEx(elem.path,elem.destpath,None,None,False,win32file.COPY_FILE_FAIL_IF_EXISTS)
			else:
				win32file.CreateDirectory(elem.destpath)
		except win32file.error as err:
			appendRetry(op.output,elem)
			continue
		#end except
		op.output["succeeded"]+=1
	#end 削除処理
	if len(op.output["retry"]["target"])>0:
		op.output["retry"]["operation"]=VERB
		retry=len(op.output["retry"]["target"])
	#end リトライあるか
	return retry

def appendRetry(output,target):
	"""リトライするリストに追加する。"""
	output["retry"]["target"].append(target)

"""
		try:
			if os.path.isfile(elem):
				win32file.CopyFileEx(elem)
			else:
				win32file.RemoveDirectory(elem)
		except win32file.error as err:
			appendRetry(op.output,elem)
			continue
		#end except
"""