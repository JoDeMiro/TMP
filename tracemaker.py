class FilePreProcesser():

	def __init__(self, subfolder):
		print('Hello init')
		import os
		self.dirpath = os.getcwd()
		self.subfolder = subfolder
		self.fullpath = self.dirpath + self.subfolder
		print(self.fullpath)

	def concatenate_apache_web_access_logs(self):
		print('Hello concatenate_apache_web_access_logs')
		filenames = self.filenames_with_path
		with open(self.fullpath + '\\access.log', 'w') as outfile:
		    for fname in filenames:
		        with open(fname) as infile:
		            for line in infile:
		                outfile.write(line)

	def get_filenames_from_directory(self):
		print('Hello get_filenames_from_directory')
		from os import listdir
		from os.path import isfile, join

		directory_path = self.fullpath
		print(directory_path)
		onlyfiles = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]
		pathfiles = []
		for i in onlyfiles:
			pathfiles.append(self.fullpath + '\\' + i)
		self.filenames = onlyfiles
		self.filenames_with_path = pathfiles
		print(self.filenames)
		print(self.filenames_with_path)

	def read_access_log(self):
		print('Hello read_access_log')
		import re

		self.get_request_times = []

		with open(self.fullpath + '\\access.log') as f:
			a = f.readlines()
			for line in a:
				str = line
				result = re.search('- - (.*) "GET', str)
				if not (result is None):
					print(result.group(1))
					self.get_request_times.append(result.group(1)[1:-1])	# [06/Sep/2020:03:37:51 +0200] -> 06/Sep/2020:03:37:51 +0200

	def write_time_to_csv(self):
		with open(self.fullpath + '\\get_times.txt', 'w') as f:
			for item in self.get_request_times:
				f.write("%s\n" % item)

	def convert_access_log_time_to_timestamp(self):
		self.get_request_timestamps = []
		from dateutil import parser
		for i in self.get_request_times:
			ido = parser.parse(i.replace(':', ' ', 1))
			timestamp = ido.timestamp()
			self.get_request_timestamps.append(timestamp)

	def sort_timestamps(self):
		self.get_request_timestamps.sort()

	def write_timestamps_to_csv(self):
		with open(self.fullpath + '\\get_timestamps.txt', 'w') as f:
			for item in self.get_request_timestamps:
				f.write("%s\n" % item)

	def calculate_differences(self):
		self.get_request_times_diff = []
		for i in range(len(self.get_request_timestamps)-1):
			ido1 = self.get_request_timestamps[i]
			ido2 = self.get_request_timestamps[i+1]
			diff = ido2-ido1
			self.get_request_times_diff.append(diff)

	def write_timestamp_diff_to_csv(self):
		with open(self.fullpath + '\\get_timestamps_diff.txt', 'w') as f:
			for item in self.get_request_times_diff:
				f.write("%s\n" % item)


if __name__ == "__main__":
	import os
	processer = FilePreProcesser(subfolder = '\\trace')
	processer.get_filenames_from_directory()
	processer.concatenate_apache_web_access_logs()
	processer.read_access_log()
	processer.write_time_to_csv()
	processer.convert_access_log_time_to_timestamp()
	processer.sort_timestamps()
	processer.write_timestamps_to_csv()
	processer.calculate_differences()
	processer.write_timestamp_diff_to_csv()
