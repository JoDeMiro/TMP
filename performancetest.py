import requests
import os
import time
import threading
from traceloader import TraceLoader


class PerformanceTest(object):
	"""docstring for ClassName"""

	def __init__(self, host, port):
		super(PerformanceTest, self).__init__()
		self.host = host
		self.port = port
		self.addr = self.host + ':' + self.port
	
	def check(self):
		r = requests.get(self.host + ':' + self.port)
		print(r.status_code)
		print(r.headers)
		print(r.content)

	def health(self):
		r = requests.get(self.addr + '/actuator/health')
		print('----------------------------')
		print(r.status_code)
		print(r.headers)
		print(r.content)

	def wait(self):
		r = requests.get(self.addr + '/wait')
		print('----------------------------')
		print(r.status_code)
		print(r.headers)
		print(r.content)

	def thread_function(self, name, address):
		start_time = time.time()
		r = requests.get(self.addr + address.rest)
		response_time = time.time() - start_time
		self.trace_response_times.append(response_time)
		print('----------------------------')
		print('name : ', name)
		print(r.status_code)
		print(r.headers)
		print(r.content)
		print('----------------------------')

	def tracer(self, traceloader, begin, end, multiplier, address):
		request_sequence = traceloader.get_request_times_diff[begin:end]
		print(request_sequence)
		self.trace_response_times = []
		counter = 0
		for i in request_sequence:
			counter += 1
			delay = i / multiplier
			print(delay)

			x = threading.Thread(target=self.thread_function, args=(counter, address, ))
			x.start()

			time.sleep(delay)
			print('----------------------------')
			print(self.trace_response_times)
			print('----------------------------')
		x.join()

class Address():
	def __init__(self, rest):
		self.rest = rest

if __name__ == "__main__":
	# Init endpoint
	tester = PerformanceTest('http://localhost', '8080')
	tester.health()
	tester.wait()

	# Load trace
	trace_loader = TraceLoader(subfolder = 'trace', filename = 'get_timestamps.txt')
	trace_loader.read_apache_web_access_logs()
	trace_loader.generate_request_sequences()

	# Visualize trace
	import matplotlib
	matplotlib.use('WXAgg', force=True)
	from matplotlib import pyplot as plt
	plt.plot(trace_loader.get_request_times_diff)
	plt.show()

	# Wait test
	# wait = Address('/wait')
	# tester.tracer(trace_loader, begin = 10, end = 20, multiplier = 100, address = wait)
	# print(tester.trace_response_times)

	# Wait test 2000
	# wait = Address('/wait/2000')
	# tester.tracer(trace_loader, begin = 10, end = 20, multiplier = 100, address = wait)
	# print(tester.trace_response_times)

	# Fibonacci 30 (4300ms - 1 request)
	fibonacci30 = Address('/cpu/fibonacci/30')
	tester.tracer(trace_loader, begin = 10, end = 20, multiplier = 100, address = fibonacci30)
	print(tester.trace_response_times)