# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 guredora <contact@guredora.com>
#Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

#constants��import�O�ɕK�v
import os
import sys
sys.path.append(os.getcwd())

import datetime
import glob
import hashlib
import json
import math
import PyInstaller
import shutil
import subprocess
import urllib.request
import zipfile

import diff_archiver

import constants

from tools import bumpup


class build:
	def __init__(self):
		# appVeyor���ǂ����𔻕ʂ��A�������X�^�[�g
		appveyor = self.setAppVeyor()
		print("Starting build for %s(appveyor mode=%s)" % (constants.APP_NAME, appveyor))

		# �p�b�P�[�W�̃p�X�ƃt�@�C����������
		package_path = os.path.join("dist", os.path.splitext(os.path.basename(constants.STARTUP_FILE))[0])
		if 'APPVEYOR_REPO_TAG_NAME' in os.environ:
			build_filename = os.environ['APPVEYOR_REPO_TAG_NAME']
		else:
			build_filename = 'snapshot'
		print("Will be built as %s" % build_filename)

		# pyinstaller�̃p�X������
		if not appveyor:
			pyinstaller_path = r"D:\Dev\python38\Scripts\pyinstaller.exe"
		else:
			pyinstaller_path = "%PYTHON%\\Scripts\\pyinstaller.exe"
		print("pyinstaller_path=%s" % pyinstaller_path)
		hooks_path = os.path.join(PyInstaller.__path__[0], "hooks/")
		print("hooks_path is %s" % (hooks_path))

		# locale�t�H���_�̑��݂��m�F
		if not os.path.exists("locale"):
			print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
			exit(-1)

		# �O�̃r���h���N���[���A�b�v
		self.creen(package_path)

		# appveyor�ł̃X�i�b�v�V���b�g�̏ꍇ�̓o�[�W�����ԍ����ꎞ�I�ɏ�������
		if build_filename == "snapshot" and appveyor:
			self.makeSnapshotVersionNumber()

		# �r���h
		self.makeVersionInfo()
		self.build(pyinstaller_path, hooks_path, package_path, build_filename)
		archive_name = "%s-%s.zip" % (constants.APP_NAME, build_filename)

		# �X�i�b�v�V���b�g�łȂ����
		if build_filename == "snapshot" and not appveyor:
			print("Skipping batch archiving because this is a local snapshot.")
		else:
			patch_name = self.makePatch(build_filename, archive_name)
			if constants.UPDATER_URL is not None:
				self.addUpdater(archive_name)
			self.makePackageInfo(archive_name, patch_name, build_filename)
		print("Build finished!")


	def runcmd(self,cmd):
		proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
		proc.communicate()
		return proc.poll()


	def setAppVeyor(self):
		if len(sys.argv)>=2 and sys.argv[1]=="--appveyor":
			return True
		return False

	def creen(self,package_path):
		if os.path.isdir(package_path):
			print("Clearling previous build...")
			shutil.rmtree("dist\\")
			shutil.rmtree("build\\")

	def makeSnapshotVersionNumber(self):
		#���{�W�����I�u�W�F�N�g
		JST = datetime.timezone(datetime.timedelta(hours=+9))
		#Python�͐��E�W������Z�ɑΉ����Ă��Ȃ��̂ŕ����񏈗��ŏ��؂�A�������{�W�����ɕϊ�
		dt = datetime.datetime.fromisoformat(os.environ["APPVEYOR_REPO_COMMIT_TIMESTAMP"][0:19]+"+00:00").astimezone(JST)
		major = str(dt.year)[2:4]+str(dt.month).zfill(2)
		minor = str(dt.day)
		patch = str(int(math.floor((dt.hour*3600+dt.minute*60+dt.second)/86400*1000)))
		constants.APP_VERSION = major+"."+minor+"."+patch
		constants.APP_LAST_RELEASE_DATE = str(dt.date())
		bumpup.bumpup(major+"."+minor+"."+patch, str(dt.date()))

	def makeVersionInfo(self):
		print("making version info...")
		with open("tools/baseVersionInfo.txt", mode = "r") as f:
			version_text = f.read()
		version_text = version_text.replace("%FILE_VERSION%", constants.APP_VERSION.replace(".", ","))
		version_text = version_text.replace("%PRODUCT_VERSION%", constants.APP_VERSION.replace(".", ","))
		version_text = version_text.replace("%COMPANY_NAME%", constants.APP_DEVELOPERS)
		version_text = version_text.replace("%FILE_DESCRIPTION%", constants.APP_FULL_NAME)
		version_text = version_text.replace("%FILE_VERSION_TEXT%", constants.APP_VERSION)
		version_text = version_text.replace("%REGAL_COPYRIGHT%", constants.APP_COPYRIGHT_MESSAGE)
		original_file_name = os.path.splitext(os.path.basename(constants.STARTUP_FILE))[0]+".exe"
		version_text = version_text.replace("%ORIGINAL_FILENAME%", original_file_name)
		version_text = version_text.replace("%PRODUCT_NAME%", constants.APP_NAME)
		version_text = version_text.replace("%PRODUCT_VERSION_TEXT%", constants.APP_VERSION)
		with open("version.txt", mode = "w") as f:
			f.write(version_text)

	def build(self,pyinstaller_path, hooks_path, package_path, build_filename):
		print("Building...")
		for hook in constants.NEED_HOOKS:
			shutil.copy(hook, hooks_path)
		if constants.APP_ICON == None:
			ret = self.runcmd("%s --windowed --log-level=ERROR --version-file=version.txt %s" % (pyinstaller_path, constants.STARTUP_FILE))
		else:
			ret = runcmd("%s --windowed --log-level=ERROR --version-file=version.txt --icon=%s %s" % (pyinstaller_path, constants.APP_ICON, constants.STARTUP_FILE))
		print("build finished with status %d" % ret)
		if ret != 0:
			sys.exit(ret)

		shutil.copytree("locale\\",os.path.join(package_path, "locale"), ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
		for item in constants.PACKAGE_CONTAIN_ITEMS:
			if os.path.isdir(item):
				shutil.copytree(item, os.path.join(package_path, item))
			if os.path.isfile(item):
				shutil.copyfile(item, os.path.join(package_path, os.path.basename(item)))
		for elem in glob.glob("public\\*"):
			if os.path.isfile(elem):
				shutil.copyfile(elem, os.path.join(package_path, os.path.basename(elem)))
			else:
				shutil.copytree(elem, os.path.join(package_path, os.path.basename(elem)))
		#end copypublic

		print("deleting temporary version file...")
		os.remove("version.txt")
		os.remove(os.path.splitext(os.path.basename(constants.STARTUP_FILE))[0]+".spec")

		print("Compressing into package...")
		shutil.make_archive("%s-%s" % (constants.APP_NAME, build_filename),'zip','dist')

	def makePatch(self, build_filename, archive_name):
		patch_name = None
		if constants.BASE_PACKAGE_URL is not None:
			print("Making patch...")
			patch_name = "%s-%spatch" % (constants.APP_NAME, build_filename)
			archiver=diff_archiver.DiffArchiver(constants.BASE_PACKAGE_URL, archive_name, patch_name,clean_base_package=True, skip_root = True)
			archiver.work()
		return patch_name

	def addUpdater(self, archive_name):
		print("downloading updater...")
		urllib.request.urlretrieve(constants.UPDATER_URL, "updater.zip")
		print("writing updater...")
		with zipfile.ZipFile("updater.zip", "r") as zip:
			zip.extractall()
		with zipfile.ZipFile(archive_name, mode = "a") as zip:
			zip.write("ionic.zip.dll", "%s/ionic.zip.dll" % (constants.APP_NAME))
			zip.write("updater.exe", "%s/updater.exe" % (constants.APP_NAME))
		os.remove("ionic.zip.dll")
		os.remove("updater.exe")
		os.remove("updater.zip")

	def makePackageInfo(self, archive_name, patch_name, build_filename):
		print("computing hash...")
		with open(archive_name, mode = "rb") as f:
			content = f.read()
		package_hash = hashlib.sha1(content).hexdigest()
		if constants.BASE_PACKAGE_URL is not None:
			with open(patch_name+".zip", mode = "rb") as f:
				content = f.read()
				patch_hash = hashlib.sha1(content).hexdigest()
		else:
			patch_hash = None
		print("creating package info...")
		info = {}
		info["package_hash"] = package_hash
		info["patch_hash"] = patch_hash
		info["version"] = constants.APP_VERSION
		info["released_date"] = constants.APP_LAST_RELEASE_DATE
		with open("%s-%s_info.json" % (constants.APP_NAME, build_filename), mode = "w") as f:
			json.dump(info, f)

if __name__ == "__main__":
	build()
