# -*- coding: utf-8 -*-
# Command parser
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import argparse
import json
import re

import constants

from entities import BodyField, Header, Request
from enumClasses import BodyFieldType, ContentType, HeaderFieldType, Method

class CommandParser:
	def __init__(self):
		parser = argparse.ArgumentParser(
			prog = constants.APP_NAME,
			description=_("HTTPまたはHTTPSによる通信を行います。コマンドは本家curlに近いですが、完全に再現されているわけではないことに注意してください。"),
		)

		# 結果や表示関係の処理
		#parser.add_argument("-o", "--output", help=_("出力を指定した名前のファイルに保存します。カレントディレクトリに指定した名前のファイルが既に存在した場合、上書きされます。"))
		#parser.add_argument("-O", "--remote-name", action="store_true", help=_("指定したURLのファイル名部分(パラメータを含む)をと同じ名前で出力を保存します。カレントディレクトリに指定した名前のファイルが既に存在した場合、上書きされます。URLデコードは行われないことに注意してください。"))
		#parser.add_argument("-J", "--remote-header", help=_("URLからファイル名を抽出する代わりに、レスポンス中のContent-Dispositionヘッダの内容を-O、--remote-nameオプションに指定します。指定のファイルが既に存在する場合、上書きはされずにこのオプションが無視されます。URLデコードは行われないこと、DLLなどソフトウェアから自動で読み込まれるファイルの名前を返されること等に注意してください。"))
		#parser.add_argument("-s", "--silent", action="store_true", help=_("サイレント実行。進行状況やエラーを表示しません。"))
		#parser.add_argument("-S", "--show-error", action="store_true", help=_("-s、--silentと併せて使用すると、失敗した場合にエラーメッセージが表示されます。"))
		#parser.add_argument("-v", "--verbose", action="store_true")
		#parser.add_argument("--trace-ascii", action="store_true")
		#parser.add_argument("-w", "--write-out")
		#roup = parser.add_mutually_exclusive_group()


		# 制御設定
		#リダイレクトの追跡
		#parser.add_argument("-l", "--location", action="store_true")
		#parser.add_argument("--location-trusted", action="store_true", help=_("-l、--locationと同じですが、リダイレクト先にも-u、--userで指定した内容を送信します。HTTPサイトにリダイレクトする場合、セキュリティ上の問題が生じる場合があります。"))
		#parser.add_argument("-k", "--insecure", action="store_true")


		# 内容の指定
		parser.add_argument("-d", "--data", "--data-raw", "--data-ascii",
			help=_("リクエストの本文を設定します。URLエンコードなどの前処理は行われません。")
		)
		#parser.add_argument("--data-urlencode")
		parser.add_argument("-H", "--header", action="append", default=[], 
			help=_("リクエストに追加で含めるヘッダを設定します。内部で生成されるものを上書きすることができますが、このような指定は推奨されません。" +
				"ヘッダ名だけを指定することで、設定済みのヘッダを削除できます。" +
				"値のないヘッダを送信する場合、:の代わりに;を指定します。この場合、:に置き換えて送信されます。" +
				"改行コードは自動的に挿入去れるため、引数に含めないでください。" +
				"@を使用したファイルの指定には対応していません。" +
				#"-L,--locationと併せて指定した場合、リダイレクト先にも送信されるため、セキュアな情報の指定をする際には注意してください。"
				"このオプションは、複数回指定することで複数のヘッダを指定可能です。")
		)
		#parser.add_argument("-f", "--file")
		parser.add_argument("-X", "--request", choices=[item.name for item in Method], default="", help=_("送信するメソッド名を設定します。この指定を行っても、送信するメソッド名が変わるのみであり、プログラムの動作は変更されません。-L、--locationと併せて指定した場合、リダイレクト時のステータスコードにかかわらず、すべてのリクエストにここで指定したメソッドを使用するため、意図しない動作となる場合があります。"))
		#parser.add_argument("-u", "--user", help=_("認証に使用するユーザ名とパスワードを送信します。パスワードの省略、Windows環境で利用できる高度な機能等には対応していません。"))
		#parser.add_argument("--digest", action="store_true", help=_("-u、--userで指定した情報を用いてダイジェスト認証を行います。"))
		parser.add_argument("URLs", default="", help="通信先URLを指定します。複数指定や{}・[]を用いた指定には対応していません。")

		# セッションの保存と利用
		#parser.add_argument("-c", "-cookiejar")		# 書き込み
		#parser.add_argument("-b", "--cookie")		# 読み込み



		invalid_options = {
			"--fail-early":_("複数のURLを指定して実行し、途中の通信でエラーになった場合、そこで実行を終了し、エラーを返します。終了コードによってエラーを確実に検出できるようにすることが目的のオプションですが、CADは複数のURLの指定をサポートしていないため、この指定はできません。"),
			"-f":_("ステータスコードが200以外の場合に、結果を出力せず終了コード22等で終了するオプションですが、CADでは終了コードによる結果の返却やCUIのみでの利用に対応していないため、この指定はできません。"),
			"--fail":_("ステータスコードが200以外の場合に、結果を出力せず終了コード22等で終了するオプションですが、CADでは終了コードによる結果の返却やCUIのみでの利用に対応していないため、この指定はできません。"),
			"--remote-name-all":_("複数のURLを指定した際、すべてのURLに対して-O、--remote-nameを指定するオプションですが、CADは複数のURLの指定に対応していないため、この指定はできません。"),
			"--basic": _("-u、--userと併せて指定することでベーシック認証を使用することを使用するオプションですが、この動作はデフォルトであり、CADでは対応していない複数URLの指定をしない限り使い道がないため、この指定はできません。"),
			"--negotiate": _("ネゴシエート(SPNEGO)認証を使用するオプションですが、CADは対応していません。"),
			"--abstract-unix-socket": _("Windows環境に対応していないオプションのため、使用できません。"),
			"-K":_("外部ファイルから設定を読み込んでプログラムを実行するオプションですが、CADは対応していません。"),
			"--config":_("外部ファイルから設定を読み込んでプログラムを実行するオプションですが、CADは対応していません。"),
			"-q":_("設定ファイルの読み込みを抑制するオプションですが、CADはcurl設定ファイルに対応していないため、指定できません。"),
			"--disable":_("設定ファイルの読み込みを抑制するオプションですが、CADはcurl設定ファイルに対応していないため、指定できません。"),
			"--interface":_("通信に用いるネットワークカードを指定するオプションですが、CADは対応していません。"),

		}
		#parser.add_argument()
		#parser.add_argument()
		#parser.add_argument()
		#parser.add_argument()

		self.parser = parser

	def parse_args(self):
		args =  self.parser.parse_args()

		# ヘッダ
		headers = parseHeaders(args.header)

		# メソッド
		if args.request:
			method=Method[args.request]
		else:	# 他のコマンドから推測
			# 何もなければGET
			method = Method.GET
			# -d などがあればPOST
			if args.data:
				method = Method.POST

		# ContentType
		# 基本はFORM
		contentType=ContentType.FORM
		# ヘッダでJSON指定していればJSONにする
		for item in headers:
			if item.getName().lower() == "content-type" and item.getValue().lower().startswith("application/json"):
				contentType=ContentType.JSON

		# body
		body = parseBody(args.data, contentType)

		return Request.Request("commandline request", contentType, method, args.URLs, headers, body)

def parseHeaders(headers):
	pattern = re.compile(r'^[\041-\071\073-\176]*:')	# 072=0x3A=:はダメ
	result = []
	for item in headers:
		# キーのみのヘッダ
		if re.match(r'^[\041-\071\073-\176]*;$', item):
			result.append(Header.Header(item[:-1], HeaderFieldType.CONST, ""))
			continue
		# 条件を満たさない
		elif not pattern.match(item):
			raise ValueError(_("ヘッダの指定が不正です。"))

		i = item.find(':')
		v = item[i+1:].lstrip()
		if v:
			result.append(Header.Header(item[:i], HeaderFieldType.CONST, v))
		else:
			result.append(Header.Header(item[:i], HeaderFieldType.REMOVE, ""))
	return result



def parseBody(data, contentType):
	body = []

	# 何も考えずにJSONパース
	try:
		items = json.loads(data)
		for k,v in items.items():
			if type(k) != str or type(v) not in (bool,float,int, type(None), str):
				raise ValueError(_("現在、JSONリクエストでのリストや辞書の利用はサポートしていません。"))
			body.append(BodyField.BodyField(k, BodyFieldType.CONST, v))
		return body
	except:
		if contentType == ContentType.JSON:
			raise ValueError(_("JSONデータのパースに失敗しました。"))

	if args.data and contentType == ContentType.FORM:
		for arg in args.data.split("&"):
			if not arg:
				continue
			nv = arg.split('=', 1)
			if len(nv) != 2:
				nv.append("")
		body.append(BodyField.BodyField(nv[0], BodyFieldType.ENCORDED, nv[1]))
	return body
