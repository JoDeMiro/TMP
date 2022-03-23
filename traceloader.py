class TraceLoader(object):
	"""docstring for ClassName"""

	def __init__(self, subfolder, filename):
		super(TraceLoader, self).__init__()
		import os
		self.dirpath = os.getcwd()
		self.subfolder = subfolder
		self.filename = filename
		self.fullpath = self.dirpath + '\\' + self.subfolder
		self.filename_with_path = self.fullpath + '\\' + self.filename
		print(self.fullpath)
		print(self.filename_with_path)

	def generate_request_sequences(self):
		self.get_request_times_diff = []
		for i in range(len(self.get_request_times)-1):
			ido1 = self.get_request_times[i]
			ido2 = self.get_request_times[i+1]
			diff = ido2-ido1
			self.get_request_times_diff.append(diff)
		print(self.get_request_times_diff)
		pass

	def read_apache_web_access_logs(self) -> float:
		self.get_request_times = []
		print('Hello read_apache_web_access_logs')
		file = self.filename_with_path
		with open(file) as f:
			a = f.readlines()
			for line in a:
				str = float(line[:-1])
				self.get_request_times.append(str)

