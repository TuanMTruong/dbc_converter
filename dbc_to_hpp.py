#! /usr/bin/python

import cantools as ct
import argparse



def writeLine(fd,string=''):
	fd.write(string + '\n')


parser = argparse.ArgumentParser(description='Convert CAN DBC file to C++ code.')
parser.add_argument('dbc', type=str, help='DBC file.')
parser.add_argument('-o', type=str, help='Output file', dest='out_file')
args = parser.parse_args()

dbc_filename = args.dbc
output_filename = args.out_file

messages = ct.db.load_file(dbc_filename).messages
print 'DBC file:', dbc_filename
print 'Number of messages:', len(messages)

fd = open(output_filename, 'wt')

writeLine(fd, '/******************************** DO NOT EDIT THIS FILE, IT WAS AUTOMATICALLY GENERATED ********************************/')
writeLine(fd, '#pragma once')
writeLine(fd, '#include <stdint.h>')
writeLine(fd, '#include <string.h>')
writeLine(fd)


# CAN ID table
writeLine(fd, '// ID table used for checking ID for correlating IDs.')
writeLine(fd, 'typedef enum canIDTable {')

for m in messages:
	fd.write('\t'+ m.name + '_id = ' + str(m.frame_id))
	if m == messages[-1]:
		writeLine(fd)
	else:
		writeLine(fd, ',')

writeLine(fd, '} idTable;')
writeLine(fd)


# add CAN message class
writeLine(fd, '// CAN message class to store message info')
writeLine(fd, 'class CANMessage{')
writeLine(fd, 'public:')
writeLine(fd, '\tCANMessage(){}')
writeLine(fd, '\tCANMessage(uint32_t id): id(id) {}')
writeLine(fd, '\tCANMessage(uint32_t id, bool remote, bool extended, uint8_t dlc):')
writeLine(fd, '\t\tid(id),')
writeLine(fd, '\t\tis_remote(remote),')
writeLine(fd, '\t\textended(extended),')
writeLine(fd, '\t\tdlc(dlc) {}')
writeLine(fd, '\tCANMessage(uint32_t id, bool remote, bool extended, uint8_t dlc, uint8_t* newData):')
writeLine(fd, '\t\tid(id),')
writeLine(fd, '\t\tis_remote(remote),')
writeLine(fd, '\t\textended(extended),')
writeLine(fd, '\t\tdlc(dlc) {')
writeLine(fd, '\t\t\tmemcpy(data, newData, dlc);')
writeLine(fd, '\t}')
writeLine(fd)
writeLine(fd, '\tuint32_t id;')
writeLine(fd, '\tbool is_remote;')
writeLine(fd, '\tbool extended;')
writeLine(fd, '\tuint8_t dlc;')
writeLine(fd, '\tuint8_t data[8];')
writeLine(fd, '};')
writeLine(fd)



# for each message
for m in messages:
	signals = m.signals

	# create class of message name
	writeLine(fd, '/******** ' + m.name + ' ********/')
	writeLine(fd, 'class ' + m.name + '_Message' + '{')
	writeLine(fd, 'public:')

	# static id, remote, extended, dlc
	writeLine(fd, '\tstatic constexpr uint32_t messageID = ' + str(m.frame_id) + ';')
	# TODO: find out how to get remote frame details, for now it is false
	writeLine(fd, '\tstatic constexpr bool remote = ' + 'false;')
	writeLine(fd, '\tstatic constexpr bool extended = ' + str(m.is_extended_frame).lower() + ';')
	writeLine(fd, '\tstatic constexpr uint8_t dlc = ' + str(m.length) + ';')
	writeLine(fd)

	if m.comment:
		writeLine(fd, '\t//Comment Field: ' + m.comment)
		writeLine(fd)

	# set constructors
	writeLine(fd, '\t// sets ID, remote, extended, and dlc')
	writeLine(fd, '\t' + m.name + '_Message' + '(): _msg(messageID, remote, extended, dlc) {}')
	writeLine(fd, '\t// sets ID, remote, extended, dlc, and copies passed in array.')
	writeLine(fd, '\t' + m.name + '_Message' + '(uint8_t* newData): _msg(messageID, remote, extended, dlc, newData) {}')
	writeLine(fd, '\t// Copies message pass in')
	writeLine(fd, '\t' + m.name + '_Message' + '(const CANMessage &m): _msg(m) {}')
	writeLine(fd)

	# enum class types
	for s in signals:
		if s.choices:
			writeLine(fd, '\tenum class ' + m.name + '_' + s.name + '_t' + '{')
			choiceLength = len(s.choices)
			num = 0
			for c in s.choices:
				num = num + 1;
				line = '\t\t' + s.choices[c].replace(' ','_') + ' = ' + str(c)
				if num < choiceLength:
					line = line + ','

				writeLine(fd, line)
			writeLine(fd, '\t};')
			writeLine(fd)

	# getter and setters for each signal
	for s in signals:
		writeLine(fd, '\t// ' + s.name)
		writeLine(fd, '\t// min = ' + str(s.minimum) + ' max = ' + str(s.maximum) + ' units: ' + str(s.unit) + ' scale: ' + str(s.scale))
		writeLine(fd, '\t// Signal comment: ' + s.comment)
		typeName = ''
		# check if it has a choice so set the type of it
		if s.choices:
			typeName = m.name + '_' + s.name + '_t'
		else:
			if not s.is_signed:
				typeName = typeName + 'u'
			typeName = typeName +'int' + str(s.length) + '_t'

		#getter
		writeLine(fd, '\t' + typeName + ' get' + s.name + '() const{')
		startIdx = int(s.start/8)
		sigLen = int(s.length/8)
		returnLine = ''
		if s.choices:
			returnLine = returnLine + '(' + m.name + '_' + s.name + '_t' + ')'
		if s.byte_order == 'little_endian':
			writeLine(fd, '\t\t//Little Endian')
			shiftIdx = sigLen -1
			for i in range(sigLen - 1 + startIdx, startIdx-1, -1 ):
				if shiftIdx == 0:
					returnLine = returnLine + '(_msg.data[' + str(i) + '])'
				else:
					returnLine = returnLine + '(_msg.data[' + str(i) + ']<<' + str(shiftIdx*8) + ')'
				shiftIdx = shiftIdx - 1
				if i == startIdx:
					returnLine = returnLine + ';'
				else:
					returnLine = returnLine + ' | '
		elif s.byte_order == 'big_endian':
			writeLine(fd, '\t\t//Big Endian')
			shiftIdx = sigLen -1
			for i in range(startIdx, startIdx + sigLen, 1 ):
				if shiftIdx == 0:
					returnLine = returnLine + '(_msg.data[' + str(i) + '])'
				else:
					returnLine = returnLine + '(_msg.data[' + str(i) + ']<<' + str(shiftIdx*8) + ')'
				shiftIdx = shiftIdx - 1
				if i == startIdx:
					returnLine = returnLine + ';'
				else:
					returnLine = returnLine + ' | '
		writeLine(fd, '\t\treturn ' + returnLine)
		writeLine(fd, '\t}')
		writeLine(fd)


		# setter
		writeLine(fd, '\tvoid set' + s.name + '(' + typeName + ' value){')
		startIdx = int(s.start/8)
		sigLen = int(s.length/8)
		if s.byte_order == 'little_endian':
			writeLine(fd, '\t\t//Little Endian')
			num = sigLen -1
			for i in range(startIdx, startIdx + sigLen, 1 ):
				if num == 0:
					writeLine(fd, '\t\t_msg.data[' + str(i) + '] = (uint8_t)(value);')
				else:
					writeLine(fd, '\t\t_msg.data[' + str(i) + '] = (uint8_t)(value >> ' + str(num*8) + ');')
				num = num - 1
		if s.byte_order == 'big_endian':
			writeLine(fd, '\t\t//Big Endian')
			shiftIdx = sigLen -1
			for i in range(startIdx, startIdx + igLen, 1 ):
				if num == 0:
					writeLine(fd, '\t\t_msg.data[' + str(i) + '] = (uint8_t)(value);')
				else:
					writeLine(fd, '\t\t_msg.data[' + str(i) + '] = (uint8_t)(value >> ' + str(i*8) + ');')
		writeLine(fd, '\t}')
		writeLine(fd)



	# portected can message object
	writeLine(fd, 'protected:')
	writeLine(fd, '\tCANMessage _msg;')
	writeLine(fd, '};')
	writeLine(fd)

writeLine(fd, '/**********************************************************************************************************************/')