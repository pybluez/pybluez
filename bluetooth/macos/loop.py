import asyncio
import time

import Foundation
import AppKit


class Loop():
	event_loop = None
	def __init__(self):
		self.has_event_loop = AppKit.NSRunningApplication.currentApplication().isActive()
		if not self.has_event_loop:
			self.event_loop = Foundation.NSRunLoop.mainRunLoop()

	async def wait(self, delay):
		if self.has_event_loop:
			await asyncio.sleep(delay)
		else:
			date=Foundation.NSDate.dateWithTimeIntervalSinceNow_(min(delay, 3))
			self.event_loop.runUntilDate_(date)

	def wait_blocking(self, delay):
		if self.has_event_loop:
			time.sleep(delay)
		else:
			date=Foundation.NSDate.dateWithTimeIntervalSinceNow_(min(delay, 3))
			self.event_loop.runUntilDate_(date)

	def wait_until(self, func, timeout=None):
		start_time = time.time()

		while not func():
			self.wait_blocking(0.01)
			if timeout and (time.time() - start_time) > timeout:
				return False

		return True
