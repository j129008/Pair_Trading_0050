# -*- coding: utf-8 -*-
"""
Processing the raw data of TXO, stock and Taiwan weighted index
from 2001 to 2013
"""

__author__ = 'chen hsueh-min'

import csv
import datetime
import copy
import urllib
import numpy as np
from abc import ABCMeta, abstractmethod


class AbstractDailyData:
	"""
	Class Type : Interface
	"""
	__metaclass__ = ABCMeta


class RawOptionDailyData(AbstractDailyData):
	Keys = (
	'Date', 'Contract', 'Maturity', 'Strike', 'Type', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI',
	'LastBid', 'LastOffer', 'HisHigh', 'HisLow')
	invKeys = {'Date': 0, 'Contract': 1, 'Maturity': 2, 'Strike': 3, 'Type': 4, 'Open': 5, 'High': 6, 'Low': 7,
	           'Close': 8, 'Volume': 9, 'Settlement': 10, 'OI': 11, 'LastBid': 12, 'LastOffer': 13, 'HisHigh': 14,
	           'HisLow': 15}
	# data = []

	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()

	def _processRow(self, row):
		row[self.invKeys['Date']] = self._toDate(row[self.invKeys['Date']])
		row[self.invKeys['Maturity']] = datetime.datetime.strptime(str(int(row[self.invKeys['Maturity']])),
		                                                           '%Y%m').date()
		row[self.invKeys['Type']] = 'Put' if row[self.invKeys['Type']] == '\xbd\xe6\xc5v' or row[self.invKeys[
			'Type']] == 'Put' else 'Call'

		# except 'Contract', 'Date', 'Maturity', 'Type'
		for key in (
		'Strike', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI', 'LastBid', 'LastOffer', 'HisHigh',
		'HisLow'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[self.invKeys[key]] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)  # skip the header row
			for row in reader:
				try:
					date = self._toDate(row[0])
					if date < beginDate:
						continue
					elif date > endDate:
						# Original data is sorted by date, so we can stop reading if it exceeds endDate.
						return result

					row = self._processRow(row)
				except:
					continue

				if self._validateRow(row, **kwargs):
					result.append(tuple(row))
		return result

	def getDataByDate(self, beginDate='2001/01/01', endDate='2013/12/31', **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate)
			endDate = self._toDate(endDate)

		if beginDate > endDate:
			return []

		data = []
		for year in range(beginDate.year, endDate.year + 1):
			if year == 2001:
				data += self._readDataFromCSV('Option_RawHistoData/2001_opt.csv', beginDate, endDate, **kwargs)
			else:
				data += self._readDataFromCSV(
					'Option_RawHistoData/' + str(year) + '_opt/' + str(year) + '_01_06_opt.csv',
					beginDate, endDate, **kwargs)
				data += self._readDataFromCSV(
					'Option_RawHistoData/' + str(year) + '_opt/' + str(year) + '_07_12_opt.csv',
					beginDate, endDate, **kwargs)
		return np.array(data)

	def saveAsCSV(self, data, filename):
		with open(filename, 'wb') as f:
			w = csv.writer(f)
			w.writeheader()
			for row in data:
				row = list(row)

				# Very inefficient but important! Avoiding change the content of data.
				tempDate = copy.deepcopy(row[self.invKeys['Date']])
				tempMaturity = copy.deepcopy(row[self.invKeys['Maturity']])

				row[self.invKeys['Date']] = row[self.invKeys['Date']].strftime('%Y/%m/%d')
				row[self.invKeys['Maturity']] = row[self.invKeys['Maturity']].strftime('%Y%m')
				w.writerow(row)

				row[self.invKeys['Date']] = tempDate
				row[self.invKeys['Maturity']] = tempMaturity
				del tempDate
				del tempMaturity
				row = tuple(row)

	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)  # skip the header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append(tuple(row))
		return np.array(result)


# we will consider TXO only
class TXOptionDailyData(AbstractDailyData):
	Keys = (
	'Date', 'Contract', 'Maturity', 'Strike', 'Type', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI',
	'LastBid', 'LastOffer', 'HisHigh', 'HisLow')
	invKeys = {'Date': 0, 'Contract': 1, 'Maturity': 2, 'Strike': 3, 'Type': 4, 'Open': 5, 'High': 6, 'Low': 7,
	           'Close': 8, 'Volume': 9, 'Settlement': 10, 'OI': 11, 'LastBid': 12, 'LastOffer': 13, 'HisHigh': 14,
	           'HisLow': 15}

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y-%m-%d').date()

	def _processRow(self, row):
		row[self.invKeys['Date']] = self._toDate(row[self.invKeys['Date']])
		row[self.invKeys['Maturity']] = self._toDate(row[self.invKeys['Maturity']])

		# except 'Contract', 'Date', 'Maturity', 'Type'
		for key in (
		'Strike', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI', 'LastBid', 'LastOffer', 'HisHigh',
		'HisLow'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[self.invKeys[key]] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs) and row[self.invKeys['Date']] >= beginDate and row[
					self.invKeys['Date']] <= endDate:
					result.append(tuple(row))
		return result

	def getDataByDate(self, beginDate, endDate, **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate.replace('/', '-'))
			endDate = self._toDate(endDate.replace('/', '-'))

		if beginDate > endDate:
			return np.array([])

		data = []
		for year in range(beginDate.year, endDate.year + 1):
			data += self._readDataFromCSV('Option_HistoData/TXO_' + str(year) + '.csv', beginDate, endDate, **kwargs)

		return np.array(data)


class StockDailyData(AbstractDailyData):
	Keys = ('Date', 'Volume', 'Amount', 'Open', 'High', 'Low', 'Close', 'Difference', 'NoOfTransactions')
	invKeys = {'Date': 0, 'Volume': 1, 'Amount': 2, 'Open': 3, 'High': 4, 'Low': 5, 'Close': 6, 'Difference': 7,
	           'NoOfTransactions': 8}


	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()

	def _mkToDate(self, dateStr):
		result = map(int, dateStr.split('/'))
		return datetime.datetime(result[0] + 1911, result[1], result[2]).date()

	def _processRow(self, row):
		row[self.invKeys['Date']] = self._mkToDate(row[self.invKeys['Date']])
		row[self.invKeys['Amount']] = long(row[self.invKeys['Amount']].replace(',', ''))
		row[self.invKeys['Volume']] = long(row[self.invKeys['Volume']].replace(',', ''))
		row[self.invKeys['NoOfTransactions']] = long(row[self.invKeys['NoOfTransactions']].replace(',', ''))
		for key in ('Open', 'High', 'Low', 'Close'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]])

		# I don't know why, but the raw data somewhat has distortion
		row[self.invKeys['Difference']] = row[self.invKeys['Open']] - row[self.invKeys['Close']]
		return row

	def _validateRow(self, row, **kwargs):
		if kwargs.has_key('stockNumber'):
			del kwargs['stockNumber']

		for key in list(kwargs.keys()):
			if row[self.invKeys[key]] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)  # skip the 1st header row
			next(reader)  # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs) and row[self.invKeys['Date']] >= beginDate and row[
					self.invKeys['Date']] <= endDate:
					result.append(tuple(row))
		return result

	def getDataByDate(self, beginDate, endDate, **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate)
			endDate = self._toDate(endDate)

		if beginDate > endDate:
			return np.array([])

		data = []
		for year in range(beginDate.year, endDate.year + 1):
			for month in range(1, 13):
				if year == beginDate.year and month < beginDate.month:
					continue
				if year == endDate.year and month > endDate.month:
					continue
				data += self._readDataFromCSV(
					'Stock_HistoData/stock_' + kwargs['stockNumber'] + '_' + datetime.date(year, month, 1).strftime(
						'%Y%m') + '.csv', beginDate, endDate, **kwargs)
		return np.array(data)

	def saveAsCSV(self, data, filename):
		with open(filename, 'wb') as f:
			w = csv.writer(f)
			w.writeheader()
			w.writeheader()  # write 2 header rows

			for row in data:
				row = list(row)
				tempDate = copy.deepcopy(row[self.invKeys['Date']])
				row[self.invKeys['Date']] = row[self.invKeys['Date']].strftime('%Y/%m/%d')
				w.writerow(row)
				row[self.invKeys['Date']] = tempDate
				del tempDate
				row = tuple(row)


	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)  # skip the 1st header row
			next(reader)  # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append(tuple(row))
		return np.array(result)

	def downloadAllCSVData(self, stockNumber='2330', beginYYYYMM='201401'):
		"""Download stock data by number and date."""
		if isinstance(beginYYYYMM, str):
			beginYYYYMM = datetime.datetime.strptime(beginYYYYMM, '%Y%m').date()

		for year in range(beginYYYYMM.year, datetime.datetime.today().year + 1):
			for month in range(1, 13):
				if year == beginYYYYMM.year and month < beginYYYYMM.month:
					continue
				if year == datetime.datetime.today().year and month > datetime.datetime.today().month:
					continue
				url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report' + datetime.date(
					year, month, 1).strftime('%Y%m') + '/' + datetime.date(year, month, 1).strftime(
					'%Y%m') + '_F3_1_8_' + stockNumber + '.php&type=csv'
				filename = 'Stock_HistoData/stock_' + stockNumber + '_' + datetime.date(year, month, 1).strftime(
					'%Y%m') + '.csv'
				urllib.urlretrieve(url, filename)


class IndexDailyData(AbstractDailyData):
	Keys = ('Date', 'Open', 'High', 'Low', 'Close')
	invKeys = {'Date': 0, 'Open': 1, 'High': 2, 'Low': 3, 'Close': 4}

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()

	def _mkToDate(self, dateStr):
		result = dateStr.split('/')
		result = map(int, result)
		return datetime.datetime(result[0] + 1911, result[1], result[2]).date()


	def _processRow(self, row):
		row[self.invKeys['Date']] = self._mkToDate(row[self.invKeys['Date']])
		for key in ('Open', 'High', 'Low', 'Close'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]].replace(',', ''))
		return row


	def _readDataFromCSV(self, filename, beginDate, endDate):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)  # skip the 1st header row
			next(reader)  # skip the 2nd header row
			next(reader)  # skip the 3rd header row
			for row in reader:
				try:
					row = self._processRow(row)
					if row[self.invKeys['Date']] >= beginDate and row[self.invKeys['Date']] <= endDate:
						result.append(tuple(row))
				except:
					continue

		return result


	def getDataByDate(self, beginDate, endDate):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate)
			endDate = self._toDate(endDate)

		if beginDate > endDate:
			return np.array([])

		data = []
		for year in range(beginDate.year, endDate.year + 1):
			for month in range(1, 13):
				if year == beginDate.year and month < beginDate.month:
					continue
				if year == endDate.year and month > endDate.month:
					continue
				data += self._readDataFromCSV(
					'Index_HistoData/MI_5MINS_HIST{0}{1:0>2d}'.format(year - 1911, month) + '.csv', beginDate, endDate)
		return np.array(data)


class RawFuturesDailyData(AbstractDailyData):
	Keys = ('Date', 'Contract', 'Maturity', 'Open', 'High', 'Low', 'Close')
	invKeys = {'Date': 0, 'Contract': 1, 'Maturity': 2, 'Open': 3, 'High': 4, 'Low': 5, 'Close': 6}

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()

	def _processRow(self, row):
		row[self.invKeys['Date']] = self._toDate(row[self.invKeys['Date']])
		row[self.invKeys['Maturity']] = datetime.datetime.strptime(str(int(row[self.invKeys['Maturity']])),
		                                                           '%Y%m').date()

		# except 'Contract', 'Date', 'Maturity'
		for key in ('Open', 'High', 'Low', 'Close'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]])
		return row[:len(self.Keys)]

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[self.invKeys[key]] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader)
			for row in reader:
				try:
					row = self._processRow(row)
				except:
					continue

				if self._validateRow(row, **kwargs) and row[self.invKeys['Date']] >= beginDate and row[
					self.invKeys['Date']] <= endDate:
					result.append(tuple(row))
		return result

	def getDataByDate(self, beginDate, endDate, **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate)
			endDate = self._toDate(endDate)

		if beginDate > endDate:
			return []

		data = []
		for year in range(beginDate.year, endDate.year + 1):
			data += self._readDataFromCSV('Futures_RawHistoData/' + str(year) + '_fut/' + str(year) + '_01_06_fut.csv',
			                              beginDate, endDate, **kwargs)
			data += self._readDataFromCSV('Futures_RawHistoData/' + str(year) + '_fut/' + str(year) + '_07_12_fut.csv',
			                              beginDate, endDate, **kwargs)
		return np.array(data)

	# Due to the error of raw data, remember add a space ' ' onto the end of Contract
	def refineAllRawData(self, **kwargs):
		allData = self.getDataByDate('1999/01/01', '2013/12/31', **kwargs)
		with open('Futures_HistoData/' + kwargs['Contract'].replace(' ', '') + '.csv', 'wb') as handle:
			writer = csv.writer(handle)
			for row in allData:
				row = list(row)
				writer.writerow(row)


class TXFuturesDailyData(AbstractDailyData):
	Keys = ('Date', 'Contract', 'Maturity', 'Open', 'High', 'Low', 'Close')
	invKeys = {'Date': 0, 'Contract': 1, 'Maturity': 2, 'Open': 3, 'High': 4, 'Low': 5, 'Close': 6}

	def _toDate(self, dateStr):
		return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()

	def _processRow(self, row):
		row[self.invKeys['Date']] = self._toDate(row[self.invKeys['Date']].replace('-', '/'))
		row[self.invKeys['Maturity']] = self._toDate(row[self.invKeys['Maturity']].replace('-', '/'))

		# except 'Contract', 'Date', 'Maturity'
		for key in ('Open', 'High', 'Low', 'Close'):
			row[self.invKeys[key]] = float(row[self.invKeys[key]])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[self.invKeys[key]] != kwargs[key]:
				return False
		return True

	def __init__(self):
		self.data = self._loadCSV()

	def getData(self):
		return np.array(self.data)

	def _loadCSV(self):
		result = []
		with open('Futures_HistoData/TX.csv', 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				result.append(tuple(self._processRow(row)))

		return result

	def getDataByDate(self, beginDate, endDate, near=False):
		if isinstance(beginDate, str):
			beginDate = self._toDate(beginDate)
		if isinstance(endDate, str):
			endDate = self._toDate(endDate)

		if near:
			return np.array([self.data[i] for i in range(len(self.data)) if
			        self.data[i][self.invKeys['Date']] >= beginDate and self.data[i][
				        self.invKeys['Date']] <= endDate and (
			        i == 0 or self.data[i][self.invKeys['Date']] > self.data[i - 1][self.invKeys['Date']])])
		else:
			return np.array([r for r in self.data if r[self.invKeys['Date']] >= beginDate and r[self.invKeys['Date']] <= endDate])


if __name__ == '__main__':
	oddata = TXOptionDailyData()
	data = oddata.getDataByDate('2001/01/01', '2001/12/26', Contract='TXO', Type='Call')
	# oddata.saveAsCSV( data, 'waha.csv')
	# data2 = oddata.loadCSV('waha.csv')

	sddata = StockDailyData()
	sddata.downloadAllCSVData('0050', '200306')  # Run this once is enough
