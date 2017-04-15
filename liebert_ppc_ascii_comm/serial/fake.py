import time
import liebert_ppc_ascii_comm.serial

class PpcPduSerialInterface(liebert_ppc_ascii_comm.serial.PpcPduSerialInterface):
	_cmd_buf_max_len = 8

	def __init__(self, config):
		self.config = config
		self._bad_commands = 0
		self._borked = False
		self._cmd_buffer = 'FOO' # Assume some junk in the interface
		self._cmd_buffer_size = 8

	def _debug(self, msg):
		print "DEBUG: " + repr(msg)

	def _process_command(self, query_str):
		query_str_uc = query_str.lower()

		if query_str == "time\r":
			return_str = "03:40:37A"
		elif query_str == "date?\r":
			return_str = "05-15-97"
		elif query_str == "uid?\r":
			return_str = "Unit_No._PDU_21B____<LF><CR>"
		elif query_str == "kva?\r":
			return_str = "0150"
		elif query_str == "v?\r":
			return_str = "0208"
		elif query_str == "ss1?\r":
			return_str = "UNIT_MODEL_NUMBER___,SERIAL_NUMBER_______,SITE_ID_NUMBER______,TAG_NUMBER__________"	
		elif query_str == "sa?\r":
			return_str = "02,OUTPUT_OVERVOLTAGE__,05-15-97,01:25:30A,OUTPUT_OVERCURRENT__,05-15-97,01:27:46A"
		elif query_str == "upmd?\r":
			return_str = "0484,0485,0483,0210,0212,0211,0121,0122,0121,0068,0085,0120,0131," + \
				"0018,0030,0092,0033,0600,0038,0041,0043,0549,0632,0599,00001528,0018,0019,0020,0045,0047,0049,0044"
		else:
			self._debug("Unrecognized command '%s'" % query_str)
			return False

		return return_str + "\n\r"

	def _query_timeout(self):
		time.sleep(5)
		raise Exception("Timeout!")

	def query(self, query_str):

		""" Simulate PPC interface. If we sent more than buf_len chars w/o a 
		carriage return then hang the whole interface to simulate what can happen
		on a real PPC """

		return_str=None

		if self._borked:
			self._debug("PDU borked!")
			self._query_timeout()

		# Append what we got onto the buffer
		self._cmd_buffer += query_str
		self._debug("cmd buffer='%s'" % self._cmd_buffer)

		# Ensure we didn't just blow our buffer
		if len(self._cmd_buffer) > self._cmd_buffer_size:
			self._debug("warning! Exhausted buffer size. setting to borked")
			# Whoops... we're done
			self._borked = True
			self._query_timeout()
		
		# Find location of first carriage return
		cr_idx = self._cmd_buffer.find("\r")
		self._debug("cr_idx=%d" % cr_idx)

		# Did we find a carriage return?
		if cr_idx > -1:
			# Ok, process the command
			pending_cmd = self._cmd_buffer[0:cr_idx+1]
			remaining_buf = self._cmd_buffer[cr_idx+1:]

			self._debug("processing command '%s' leaving '%s' on the buffer" % (pending_cmd, remaining_buf))
			return_str=self._process_command(pending_cmd)
			self._cmd_buffer = remaining_buf

		if return_str:
			return return_str
		else:
			self._query_timeout()


