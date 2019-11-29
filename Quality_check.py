# This program checks the quality of the video being sent
# The values mentioned in this program are taken from QVS paper
# The R- Value must be maintained above the threshold value of 50 to get a good stream

import math

def QualityCheck(dupsetting, packetloss, codec):

	dataLoss = ((1- dupsetting) * (packetloss)) + ((dupsetting * packetloss * packetloss))
	
	if codec == 4:
		x = 13.30
		b = 8.28
		X = 5.21

	elif codec == 3:
		x = 25.38
		b = 6.08
		X = 4.15

	elif codec == 2:
		x = 40.37
		b = 2.75
		X = 6.58


	voiceLoss = x + b * (math.log(1+(X*dataLoss)))
	rValue = 93.2 - voiceLoss

	return rValue

def Injection_Rate(dupsetting, codec):

	if codec == 4:
		compression = 0.25
	elif codec == 3:
		compression = 0.1875
	else:
		compression = 0.125

	injectionRate = 64 * compression * (1+dupsetting)

	return injectionRate