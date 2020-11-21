import logging
import os

from ignis.executor.core.modules.impl.IBaseImpl import IBaseImpl
from ignis.executor.core.storage import IMemoryPartition, IRawMemoryPartition, IDiskPartition, IPartitionGroup

logger = logging.getLogger(__name__)


class ICacheImpl(IBaseImpl):

	def __init__(self, executor_data):
		IBaseImpl.__init__(self, executor_data)
		self.__next_context_id = 11
		self.__context = dict()
		self.__cache = dict()

	def __fileCache(self):
		return self._executor_data.infoDirectory() + "/cache" + str(
			self._executor_data.getContext().executorId()) + ".bak"

	def saveContext(self):
		try:
			if len(self.__context) <= 10:
				for i in range(0, 11):
					if i not in self.__context.keys():
						id = i
						break
			else:
				id = self.__next_context_id
				self.__next_context_id += 1
			logger.info("CacheContext: saving context " + str(id))
			self.__context[id] = self._executor_data.getPartitions()
			return id
		except Exception as ex:
			self._pack_exception(ex)

	def clearContext(self):
		try:
			self._executor_data.deletePartitions()
			self._executor_data.clearVariables()
		except Exception as ex:
			self._pack_exception(ex)

	def loadContext(self, id):
		try:
			value = self.__context.get(id, None)
			if value and value == self._executor_data.getPartitions():
				del self.__context.get[id]
				return
			logger.info("CacheContext: loading context " + str(id))

			if not value:
				raise ValueError("context " + str(id) + " not found")
			self._executor_data.setPartitions(value)
			del self.__context.get[id]
		except Exception as ex:
			self._pack_exception(ex)

	def cache(self, id, level):
		try:
			if level == 0:  # NO_CACHE
				value = self.__cache.get(id, None)
				if not value:
					logger.warning("CacheContext: removing non existent cache " + str(id))
					return
				del self.__cache[id]
				if self._executor_data.getPartitionTools().isDisk(value):
					cache = self.__fileCache()
					found = False
					lines = list()
					with open(cache, "rb") as file_cache:
						for line in file_cache:
							if found and not line.startswith(str(2).encode() + b'\0'):
								lines.append(line)
					with open(cache, "wb") as file_cache:
						for line in lines:
							file_cache.writelines(lines)
				return

			group_cache = self._executor_data.getPartitions()
			level_sel = level

			if level == 1:  # PRESERVE
				if self._executor_data.getPartitionTools().isDisk(group_cache):
					level_sel = 4
				elif self._executor_data.getPartitionTools().isRawMemory(group_cache):
					level_sel = 3
				else:
					level_sel = 2

			if level_sel == 2:  # MEMORY
				logger.info("CacheContext: saving partition in " + IMemoryPartition.TYPE + " cache")
				if not self._executor_data.getPartitionTools().isMemory(group_cache):
					group = IPartitionGroup()
					for part_cache in group_cache:
						part = self._executor_data.getPartitionTools().newMemoryPartition(part_cache.size())
						part_cache.copyTo(part)
						group.add(part)
					group_cache = group
			elif level_sel == 3:  # RAW_MEMORY
				logger.info("CacheContext: saving partition in " + IRawMemoryPartition.TYPE + " cache")
				if not self._executor_data.getPartitionTools().isRawMemory(group_cache):
					group = IPartitionGroup()
					for part_cache in group_cache:
						part = self._executor_data.getPartitionTools().newRawMemoryPartition(part_cache.bytes())
						part_cache.copyTo(part)
						group.add(part)
					group_cache = group

			elif level_sel == 3:  # DISK
				if self._executor_data.getPartitionTools().isRawMemory(group_cache):
					for part_cache in group_cache:
						part_cache.persist(True)
				else:
					group = IPartitionGroup()
					for part_cache in group_cache:
						part = self._executor_data.getPartitionTools().newDiskPartition(persist=True)
						part_cache.copyTo(part)
						group.add(part)
					group_cache = group

				with open(self.__fileCache(), "ab") as file_cache:
					file_cache.write(str(id).encode())
					file_cache.write(b'\0')
					for part_cache in group_cache:
						file_cache.write(b'\0')
						file_cache.write(part_cache.getpath().encode())
					file_cache.write(b'\n')
			else:
				raise ValueError("CacheContext: cache level " + str(level) + " is not valid")

			self.__cache = group_cache

		except Exception as ex:
			self._pack_exception(ex)

	def loadCacheFromDisk(self):
		cache = self.__fileCache()
		if os.path.exists(cache):
			logger.info("CacheContext: cache file found, loading")
			with open(cache, "rb") as file_cache:
				for line in file_cache:
					fields = line.split(b'\0')
					id = int(fields[0])
					group = IPartitionGroup()
					for path in fields[2:]:
						group.add(IDiskPartition(path, compression=0, native=False, persist=True, read=True))
					self.__cache[id] = group

	def loadCache(self, id):
		try:
			logger.info("CacheContext: loading partition from cache")
			value = self.__cache.get(id, None)
			if not value:
				raise ValueError("cache " + str(id) + " not found")
			self._executor_data.setPartitions(value)
		except Exception as ex:
			self._pack_exception(ex)
