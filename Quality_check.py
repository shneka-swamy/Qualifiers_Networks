# This program checks the quality of the video being sent
# The values mentioned in this program are taken from QVS paper
# The R- Value must be maintained above the threshold value of 50 to get a good stream

import math

def QualityCheck(dupsetting, packetloss, codec):

	dataLoss = ((1- dupsetting) * (packetloss)) + ((dupsetting * packetloss * packetloss))
	print(dataLoss)
	
	if codec == 4:
		x = 13.30
		b = 8.28
		X = 5.21
		compression = 0.25

	elif codec == 3:
		x = 25.38
		b = 6.08
		X = 4.15
		compression = 0.1875

	elif codec == 2:
		x = 40.37
		b = 2.75
		X = 6.58
		compression = 0.125

	print((math.log(1+(X*dataLoss))))


	voiceLoss = x + b * (math.log(1+(X*dataLoss)))
	injectionRate = 64 * compression * (1+dupsetting)
	rValue = 93.2 - voiceLoss

	print(voiceLoss)
	print(injectionRate)
	print(rValue)

