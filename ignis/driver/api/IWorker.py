import ignis.rpc.driver.exception.ttypes
from ignis.driver.api.IDataFrame import IDataFrame
from ignis.driver.api.IDriverException import IDriverException
from ignis.driver.api.ISource import ISource
from ignis.driver.api.Ignis import Ignis


class IWorker:

	def __init__(self, cluster, type, name=None, cores=None):
		self.__cluster = cluster
		try:
			with Ignis._pool.getClient() as client:
				if name is None:
					if cores is None:
						self._id = client.getWorkerService().newInstance(cluster._id, type)
					else:
						self._id = client.getWorkerService().newInstance3b(cluster._id, type, cores)
				else:
					if cores is None:
						self._id = client.getWorkerService().newInstance3a(cluster._id, name, type)
					else:
						self._id = client.getWorkerService().newInstance3(cluster._id, name, type, cores)
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def start(self):
		try:
			with Ignis._pool.getClient() as client:
				client.getWorkerService().start(self._id)
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def destroy(self):
		try:
			with Ignis._pool.getClient() as client:
				client.getWorkerService().destroy(self._id)
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def getCluster(self):
		return self.__cluster

	def setName(self, name):
		try:
			with Ignis._pool.getClient() as client:
				client.getWorkerService().setName(self._id, name)
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def parallelize(self, data, partitions, src=None, native=False):
		try:
			data_id = Ignis._driverContext().parallelize(data, native)
			with Ignis._pool.getClient() as client:
				if src is None:
					return IDataFrame(client.getWorkerService().parallelize(self._id, data_id, partitions))
				else:
					src = ISource.wrap(src)
					return IDataFrame(client.getWorkerService().parallelize(self._id, data_id, partitions, src.rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def importDataFrame(self, data, partitions=None, src=None):
		try:
			with Ignis._pool.getClient() as client:
				if partitions:
					if src is None:
						return IDataFrame(client.getWorkerService().importDataFrame3a(self._id, data, partitions))
					else:
						src = ISource.wrap(src)
						return IDataFrame(
							client.getWorkerService().importDataFrame4(self._id, data, partitions, src.rpc()))
				else:
					if src is None:
						return IDataFrame(client.getWorkerService().importDataFrame(self._id, data))
					else:
						src = ISource.wrap(src)
						return IDataFrame(client.getWorkerService().importDataFrame3b(self._id, data, src.rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def textFile(self, path, minPartitions=None):
		try:
			with Ignis._pool.getClient() as client:
				if minPartitions is None:
					return IDataFrame(client.getWorkerService().textFile(self._id, path))
				else:
					return IDataFrame(client.getWorkerService().textFile3(self._id, path, minPartitions))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def partitionObjectFile(self, path, src=None):
		try:
			with Ignis._pool.getClient() as client:
				if src is None:
					return IDataFrame(client.getWorkerService().partitionObjectFile(self._id, path))
				else:
					src = ISource.wrap(src)
					return IDataFrame(client.getWorkerService().partitionObjectFile3(self._id, path, src.rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def partitionTextFile(self, path):
		try:
			with Ignis._pool.getClient() as client:
				return IDataFrame(client.getWorkerService().partitionTextFile(self._id, path))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def partitionJsonFile(self, path, src=None, objectMapping=False):
		try:
			with Ignis._pool.getClient() as client:
				if src is None:
					return IDataFrame(client.getWorkerService().partitionJsonFile3a(self._id, path, objectMapping))
				else:
					src = ISource.wrap(src)
					return IDataFrame(client.getWorkerService().partitionJsonFile3b(self._id, path, src.rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def loadLibrary(self, path):
		try:
			with Ignis._pool.getClient() as client:
				client.getWorkerService().loadLibrary(self._id, path)
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def execute(self, src):
		try:
			with Ignis._pool.getClient() as client:
				client.getWorkerService().execute(self._id, ISource.wrap(src).rpc())
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def executeTo(self, src):
		try:
			with Ignis._pool.getClient() as client:
				return IDataFrame(client.getWorkerService().executeTo(self._id, ISource.wrap(src).rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def voidCall(self, src, data=None, **kwargs):
		try:
			src = ISource.wrap(src)
			for name, var in kwargs.items():
				src.addParam(name, var)
			with Ignis._pool.getClient() as client:
				if data is None:
					client.getWorkerService().voidCall(self._id, src.rpc())
				else:
					client.getWorkerService().voidCall3(self._id, data._id, src.rpc())
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)

	def call(self, src, data=None, **kwargs):
		try:
			src = ISource.wrap(src)
			for name, var in kwargs.items():
				src.addParam(name, var)
			with Ignis._pool.getClient() as client:
				if data is None:
					return IDataFrame(client.getWorkerService().call(self._id, src.rpc()))
				else:
					return IDataFrame(client.getWorkerService().call3(self._id, data._id, src.rpc()))
		except ignis.rpc.driver.exception.ttypes.IDriverException as ex:
			raise IDriverException(ex.message, ex._cause)
