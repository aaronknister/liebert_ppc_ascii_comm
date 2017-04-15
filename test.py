#!/usr/bin/python
import liebert_ppc_ascii_comm.serial.fake

f = liebert_ppc_ascii_comm.serial.fake.PpcPduSerialInterface([])

# Test initial query, should fail
try:
	f.query("ss1?\r")
except Exception, e:
	print e

# Test subsequent query, should succeed
print f.query("ss1?\r")

# Try to overrun the buffer, even w/ a valid command, shoudl fail
try:
	print f.query("adslkf\rss1?\r")
except Exception, e:
	print e

# Try additional jibberish, should fail
try:
	print f.query("adslkfjalsdfkjaldksfjalkdfjalksdj\r")
except Exception, e:
	print e

# Try real command, should fail
try:
	print f.query("ss1?\r")
except Exception, e:
	print e
