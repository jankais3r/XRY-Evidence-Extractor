# Jan Kaiser (c) 2022
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#	1. The origin of this software must not be misrepresented; you must not
#	claim that you wrote the original software. If you use this software
#	in a product, an acknowledgment in the product documentation would be
#	appreciated but is not required.
#
#	2. Altered source versions must be plainly marked as such, and must not be
#	misrepresented as being the original software.
#
#	3. This notice may not be removed or altered from any source
#	distribution.

import xry
import io
import os
import csv
import time
import zipfile
import datetime

__contact__ = "https://github.com/jankais3r/XRY-Evidence-Extractor"
__version__ = "0.4"
__description__ = "Creates a ZIP archive with logical evidence that can be parsed by other forensic tools"

# ʕᵔᴥᵔʔ Monkey-patching a zipfile function that usually just warns about duplicate files to skip them entirely.
def monkeyWritecheck(self, zinfo):
		"""Check for errors before writing a file to the archive."""
		if zinfo.filename in self.NameToInfo:
			#import warnings
			#warnings.warn('Duplicate name: %r' % zinfo.filename, stacklevel=3)
			raise ValueError('dupes? k no thx')
		if self.mode not in ('w', 'x', 'a'):
			raise ValueError("write() requires mode 'w', 'x', or 'a'")
		if not self.fp:
			raise ValueError('Attempt to write ZIP archive that was already closed')
		zipfile._check_compression(zinfo.compress_type)
		if not self._allowZip64:
			requires_zip64 = None
			if len(self.filelist) >= ZIP_FILECOUNT_LIMIT:
				requires_zip64 = 'Files count'
			elif zinfo.file_size > ZIP64_LIMIT:
				requires_zip64 = 'Filesize'
			elif zinfo.header_offset > ZIP64_LIMIT:
				requires_zip64 = 'Zipfile size'
			if requires_zip64:
				raise LargeZipFile(requires_zip64 + ' would require ZIP64 extensions')
zipfile.ZipFile._writecheck = monkeyWritecheck

# We need this to calculate the remaining RAM. Source: https://stackoverflow.com/a/31546725
from ctypes import Structure, c_int32, c_uint64, sizeof, byref, windll
class MemoryStatusEx(Structure):
	_fields_ = [
		('length', c_int32),
		('memoryLoad', c_int32),
		('totalPhys', c_uint64),
		('availPhys', c_uint64),
		('totalPageFile', c_uint64),
		('availPageFile', c_uint64),
		('totalVirtual', c_uint64),
		('availVirtual', c_uint64),
		('availExtendedVirtual', c_uint64)]
	def __init__(self):
		self.length = sizeof(self)

def writeToFile():
	global logText, fileBuffer
	with zipfile.ZipFile(os.path.join(outputDir, 'Extracted_' + time.strftime('%Y-%m-%d %H_%M_%S', time.gmtime(startTime)) + '_v' + __version__ + '.zip'), mode = 'a') as zf:
		for f in fileBuffer:
			itemName = f[0]
			itemPath = f[1]
			itemXRYModified = f[2]
			itemSize = f[4]
			
			if len(itemName) > 0 and len(itemPath) > 0:
				try:
					itemXRYModified = str(itemXRYModified[0])
					itemZIPModified = itemXRYModified[:itemXRYModified.find(' UTC')]
					if itemZIPModified[1] == '/':
						itemZIPModified = '0' + itemZIPModified
					if itemZIPModified[4] == '/':
						itemZIPModified = itemZIPModified[:3] + '0' + itemZIPModified[3:]
					if itemZIPModified[12] == ':':
						itemZIPModified = itemZIPModified[:11] + '0' + itemZIPModified[11:]
					itemZIPModified = time.localtime(datetime.datetime.strptime(itemZIPModified, '%m/%d/%Y %I:%M:%S %p').timestamp())
					status = 'OK'
					reason = 'OK'
					info = zipfile.ZipInfo(str(itemPath[0]) + str(itemName[0]), date_time = itemZIPModified)
					zf.writestr(info, f[3].getvalue())
					itemZIPModified = datetime.datetime.fromtimestamp(time.mktime(itemZIPModified)).strftime('%Y-%m-%d %H:%M:%S')
				except ValueError: # Triggers on the monkey-patched function on duplicate item entry.
					status = 'Skipped file'
					reason = 'Extracted child item (Extracted archive item)'
					itemXRYModified = ''
					itemZIPModified = ''
				except Exception as e: # Triggers on all other items with no Date Modified, which is an indication of XRY synthesised item.
					#print(e) # If you are getting weird results (e.g., 0 files exported), uncomment this print() to see why the files fail to be exported.
					status = 'Skipped file'
					reason = 'Extracted child item (Synthesised XRY item)'
					itemXRYModified = ''
					itemZIPModified = ''
			else: # We are not interested in "files" that do not have a Path or File Name.
				status = 'Skipped file'
				reason = 'Missing Path or Name'
				itemZIPModified = ''
				try:
					itemXRYModified = str(itemXRYModified[0])
				except:
					itemXRYModified = ''
			try:
				itemPath = str(itemPath[0])
			except:
				itemPath = ''
			try:
				itemName = str(itemName[0])
			except:
				itemName = ''
			logText += '"' + status + '","' + reason + '","' + itemPath + '","' + itemName + '","' + itemXRYModified + '","' + itemZIPModified + '","' + itemSize + '"\n'
	fileBuffer = []

def parseRecursive(image, node, item):
	global logText, fileBuffer
	try:
		items = image.get_children(item[0])
	except:
		items = image.get_children(item)
	
	for i in range(len(items)):
		itemName = image.get_properties_of_type(items[i], xry.proptypes.file_name)
		itemPath = image.get_properties_of_type(items[i], xry.proptypes.file_path)
		itemData = image.get_properties_of_type(items[i], xry.proptypes.raw_data)
		itemXRYModified = image.get_properties_of_type(items[i], xry.proptypes.modified)
		
		try:
			mem = image.create_memifc(itemData[0])
			itemBytes = io.BytesIO(mem[:])
			itemSize = itemBytes.getbuffer().nbytes
		except:
			itemBytes = None
			itemSize = 0
		
		m = MemoryStatusEx()
		windll.kernel32.GlobalMemoryStatusEx(byref(m))
		if (m.availPhys / (1024.)**3) <= memoryMargin:
			print('Reached the set memory margin limit (' + str(memoryMargin) + ' GB). Writing in-memory files to disk.')
			writeToFile()
			fileBuffer.append([itemName, itemPath, itemXRYModified, itemBytes, str(itemSize)])
		else:
			fileBuffer.append([itemName, itemPath, itemXRYModified, itemBytes, str(itemSize)])
		parseRecursive(image, node, items[i])

outputDir = os.path.join(os.path.expanduser('~'), 'Desktop')
fileBuffer = []
memoryMargin = 3 # The script will write files held in memory to disk once the computer only has this amount of RAM (in GB) available.
startTime = time.time()
logText = '"Status","Reason","Path","Filename","XRY Date Modified","ZIP Date Modified","Size"\n'

def main(image, node):
	volumeRoots = image.get_children(xry.nodeids.roots.volume_root)
	for volumeRoot in volumeRoots:
		parseRecursive(image, node, volumeRoot)
		writeToFile()
	runTime = int(round(time.time() - startTime))
	with open(os.path.join(outputDir,  'Extracted_' + time.strftime('%Y-%m-%d %H_%M_%S', time.gmtime(startTime)) + '_v' + __version__ + '_log.csv'), 'w', encoding = 'utf8', errors = 'ignore') as lf:
		lf.write(logText)
	logDict = csv.DictReader(io.StringIO(logText))
	encountered = 0
	exported = 0
	for r in logDict:
		encountered += 1
		if r['Status'] == 'OK':
			exported += 1
	print('Created  Extracted_' + time.strftime('%Y-%m-%d %H_%M_%S', time.gmtime(startTime)) + '.zip in ' + outputDir)
	print(f'Processed {encountered:,d} case items. Exported {exported:,d} files. Time spent ' + str(datetime.timedelta(seconds = runTime)) + '.')
	print('Done. See log for details.')