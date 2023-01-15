# -*- coding: utf-8 -*-
# サービスプロバイダDAO

import pickle
import traceback

import constants

from logging import getLogger

log = getLogger("%s.%s" % (constants.LOG_PREFIX, "ServiceProviderDao"))


class ServiceProviderDao:

	@classmethod
	def loadAll(cls):
		log.debug("loading list to " + constants.SERVICE_PROVIDERS_FILE_NAME)
		try:
			with open(constants.SERVICE_PROVIDERS_FILE_NAME, 'rb') as f:
				return pickle.load(f)
		except FileNotFoundError:
			log.info("file not found")
			return []
		except Exception as e:
			log.error(traceback.format_exc())
			print(traceback.format_exc())
			raise e

	@classmethod
	def saveAll(cls, itemList):
		log.debug("saving list to " + constants.SERVICE_PROVIDERS_FILE_NAME)
		try:
			with open(constants.SERVICE_PROVIDERS_FILE_NAME, 'wb') as f:
				pickle.dump(itemList, f)
		except Exception as e:
			log.error(traceback.format_exc())
			print(traceback.format_exc())
			raise e
