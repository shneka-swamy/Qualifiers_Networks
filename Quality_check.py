# This program checks the quality of the video being sent
# The R- Value must be maintained above the threshold value of 50 to get a good stream

import numpy as np

def QualityCheck(dupsetting, packetloss, codec):

	dataLoss = ((1- dupsetting) * (packetloss)) + (dupsetting * packetloss * packetloss)
	
	if codec == 4:
		x = 6.50
		b = 8.28
		X = 5.21
		compression = 0.25

	elif codec == 3:
		x = 18.58
		b = 6.08
		X = 4.15
		compression = 0.1875

	elif codec == 2:
		x = 33.57
		b = 2.75
		X = 6.58
		compression = 0.125

	voiceLoss = x + (b * (np.log(1+(X*dataLoss))))
	injectionRate = 64 * compression * (1+dupsetting)
	rValue = 94.2 - voiceLoss

	print(voiceLoss)
	print(injectionRate)
	print(rValue)

def main():
	QualityCheck(0, 0.1, 3)


if __name__ == '__main__':
	main()
