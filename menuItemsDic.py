
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"FILE_SERVICE_PROVIDER":_("サービスプロバイダ一覧")+"...",
	"FILE_NEW_REQUEST":_("新規リクエスト(&N)")+"...",
	"FILE_REQUEST_HISTORY":_("履歴(&H)")+"...",

	"OPTION_OPTION":_("オプション(&O)")+"...",
	"OPTION_KEY_CONFIG":_("ショートカットキーの設定(&K)")+"...",

	"HELP_UPDATE":_("最新バージョンを確認(&U)")+"...",
	"HELP_VERSIONINFO":_("バージョン情報(&V)")+"...",

	# Request History Dialog
	"HISTORY_COPY_CURL_COMMAND":_("curlコマンドとしてコピー(&C)"),
}
