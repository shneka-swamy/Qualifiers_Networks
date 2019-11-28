# This is an implementation of ADPCM encoder.
# This code is written in reference to Microchip code

# This file contains the global variables used in the program

# Now the encoder works for 8 bit, change the code to fit 4 bit and 2 bits
import globval as gv
import pyaudio
import wave
import sys

# The list received is of order prevsample, previndex, code
def send_sample_encoder(codec, check_list):
	final_file = [check_list[0]]
	send_list = [check_list[0], 0, 0]

	for i in range(1, len(check_list)):
		send_list = ADPCM_encoder(codec, check_list[i], send_list)
		#print(send_list)
		final_file.append(send_list[2])

	return final_file

def inverse_quantizer(codec, code, step):
	# Inverse quantize the ADPCM code into predicted difference using the quantizer
	# step size

	if codec == 4:
		diffq = step >> 3
	elif codec == 3:
		diffq = step >> 2
	else:
		diffq = step >> 1

	if (codec == 4 and code & 4) or (codec == 3 and code & 2) or (codec == 2 and code & 1):
		diffq += step
	if (codec == 4 and code & 2) or (codec == 3 and code & 1):
		diffq += step >> 1
	if (codec == 4 and code & 1):
		diffq += step >> 2

	return diffq

def get_predicted_value(codec, predsample, code, diffq):
	# Find the new predicted value by adding or subtracting the diffq
	if (codec == 4 and code & 8) or (codec == 3 and code & 4) or (codec == 2 and code & 2):
		predsample -= diffq
	else:
		predsample += diffq

	# Checking overflow
	if predsample > 32767:
		predsample = 32767
	elif predsample < -32768:
		predsample = -32768

	return predsample

def get_index_value(codec, index, code):
	# Find the new stepsize and index value
	if codec == 4:
		index += gv.IndexTable_8[code]
	elif codec == 3:
		index += gv.IndexTable_4[code]
	else:
		index += gv.IndexTable_2[code]

	if index < 0:
		index = 0
	if index > 88:
		index = 88
	
	return index


def ADPCM_encoder(codec, sample, send_list):
	
	# To get the previous values set as a variable
	predsample = send_list[0]
	index = send_list[1]
	step = gv.StepSizeTable[index]

	# Compute the difference between actual and predicted sample
	diff = sample - predsample

	if diff >= 0:
		code = 0
	else:

		if codec == 4:
			code = 8
		elif codec  == 3:
			code = 4
		elif codec == 2:
			code = 2

		diff = -diff
	
	# Quantize the difference into 4 bit ADPCM code using the quanitzer step size
	tempstep = step
	if diff >= tempstep:
		
		if codec == 4:
			code |= 4
		elif codec == 3:
			code |= 2
		elif codec == 2:
			code |= 1

		diff -= tempstep
	
	tempstep >>= 1
	if diff >= tempstep:
		
		if codec == 4:
			code |= 2
		elif codec == 3:
			code |= 1

		diff -= tempstep

	tempstep >>= 1
	if diff >= tempstep:

		if codec == 4:
			code |= 1

	diffq = inverse_quantizer(codec, code, step)
	predsample = get_predicted_value(codec, predsample, code, diffq)
	index = get_index_value(codec, index, code)

	if codec == 4:
		code &= 0x0f
	elif codec == 3:
		code &= 0x07
	else:
		code &= 0x03

	send_list = [predsample, index, code]

	return send_list

def send_sample_decoder(codec, check_list):
	original_file = [check_list[0]]
	received_list = [check_list[0], 0]

	for i in range(1, len(check_list)):
		received_list = ADPCM_decoder(codec, check_list[i], received_list)
		original_file.append(received_list[0])

	return original_file


def ADPCM_decoder(codec, code, send_list):
	predsample = send_list[0]
	index = send_list[1]

	step = gv.StepSizeTable[index]

	diffq = inverse_quantizer(codec, code, step)
	predsample = get_predicted_value(codec, predsample, code, diffq)
	index = get_index_value(codec, index, code)

	send_list = [predsample, index]

	return send_list


# Find the number of 100 bytes packets and print it
def main():

    rf = wave.open(sys.argv[1], 'rb')

    p = pyaudio.PyAudio()

    data = rf.readframes(CHUNK)

    print(len(data))

    codec_1 = 2
    codec_2 = 3
    codec_3 = 4


    converted_file_1 = send_sample_encoder(codec_1, data)
   
    converted_file_2 = send_sample_encoder(codec_2, data)


    converted_file_3 = send_sample_encoder(codec_3, data)


    original_file = send_sample_decoder(codec_1, converted_file_1)
    print(len(original_file))
    print(original_file)




if __name__ == '__main__':
	main()
