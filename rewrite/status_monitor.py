

import logging
import rewrite.database
import abc

class StatusMixin(metaclass=abc.ABCMeta):

	# Abstract class (must be subclassed)
	__metaclass__ = abc.ABCMeta


	@abc.abstractmethod
	def pluginName(self):
		return None

	@abc.abstractmethod
	def db(self):
		return None


	def __init__(self):
		super().__init__()

		self.log = logging.getLogger("Main.%s.StatusMgr" % self.pluginName)


	def updateValue(self, sitename, key, value):

		with self.db.context_sess() as sess:
			row = sess.query(self.db.ScraperStatus)                  \
				.filter(self.db.ScraperStatus.site_name == sitename) \
				.scalar()

			if not row:
				row = self.db.ScraperStatus(site_name=sitename)
				sess.add(row)

			if key == 'nextRun':
				row.next_run = value
			elif key == 'prevRun':
				row.prev_run = value
			elif key == 'prevRunTime':
				row.prev_run_time = value
			elif key == 'isRunning':
				row.is_running = value
			else:
				self.log.error("Unknown key to update: '%s' -> '%s'", key, value)

			sess.commit()

	def getValue(self, sitename, key):

		with self.db.context_sess() as sess:
			row = sess.query(self.db.ScraperStatus)                  \
				.filter(self.db.ScraperStatus.site_name == sitename) \
				.scalar()

			if not row:
				row = self.db.ScraperStatus(site_name=sitename)
				sess.add(row)

			if key == 'nextRun':
				ret = row.next_run
			elif key == 'prevRun':
				ret = row.prev_run
			elif key == 'prevRunTime':
				ret = row.prev_run_time
			elif key == 'isRunning':
				ret = row.is_running
			else:
				self.log.error("Unknown key to fetch: '%s'", key)

			sess.commit()

		return ret

	def updateNextRunTime(self, name, timestamp):
		self.updateValue(name, "nextRun", timestamp)

	def updateLastRunStartTime(self, name, timestamp):
		self.updateValue(name, "prevRun", timestamp)

	def updateLastRunDuration(self, name, timeDelta):
		self.updateValue(name, "prevRunTime", timeDelta)

	def updateRunningStatus(self, name, state):
		self.updateValue(name, "isRunning", state)

	def getRunningStatus(self, name):
		return self.getValue(name, "isRunning")

class StatusResetter(StatusMixin):

	db = rewrite.database
	pluginName = None

	def __init__(self):
		super().__init__()
		self.log = logging.getLogger("Main.StatusMgr")

	def resetRunState(self):
		with self.db.context_sess() as sess:
			rows = sess.query(self.db.ScraperStatus).all()
			for row in rows:
				if row.is_running:
					self.log.info("Resetting run-state flag for %s", row.site_name)
					row.is_running = False
					sess.commit()

