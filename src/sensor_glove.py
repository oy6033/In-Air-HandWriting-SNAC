

import sys
import time
import numpy as np
import matplotlib.pyplot as plt

import serial


def recv_payload(payload_len, serial_dev):

	payload = ser.read(payload_len)

	#print(payload)

	ts = int.from_bytes(payload[0:4], byteorder='little')

	sample = np.frombuffer(payload[4:payload_len], dtype=np.float32)

	print(ts)
	print("\t", end="")
	for j in range(12):

		print("%7.4f, " % sample[j], end="")
	print()
	print("\t", end="")
	for j in range(12, 24):

		print("%7.4f, " % sample[j], end="")
	print()

	return (ts, sample)


if len(sys.argv) < 2:
	print("Missing file name!!!")
	exit(0)

fn = sys.argv[1]


ser = serial.Serial('/dev/ttyACM0', 576000)

print(ser.name)

# 0 ---> initial state, expecting magic1 (character 'A', decimal 65, hex 0x41)
# 1 ---> after magic1 is received, expecting magic2 (character 'F', decimal 70, hex 0x46)
# 2 ---> after magic2 is received, expecting a length (decimal 100, hex 0x64)
# 3 ---> after length is received, expecting an opcode (decimal 0, hex 0x00)

state = 0

stop_count = 0

data = np.zeros((2000, 25), np.float32)

i = 0

while True:

	s = ser.read(1)

	# cast the received byte to an integer	
	c = s[0]

	if state == 0:

		if c == 65:
			state = 1
		else:
			state = 0

	elif state == 1:

		if c == 70:
			state = 2
		else:
			state = 0

	elif state == 2:

		if c == 100:
			state = 3
		else:
			state = 0


	elif state == 3:

		if c == 0:

			ts, sample = recv_payload(100, ser)
			data[i, 0] = ts
			data[i, 1:] = sample

			i += 1

			# test stop condition

			amp = sample[3] * sample[3] \
				+ sample[4] * sample[4] \
				+ sample[5] * sample[5]

			if amp < 3:

				stop_count += 1
			else:

				stop_count = 0

			if stop_count > 50 or i >= 2000:

				break;

		state = 0

	else:

		print("Unknown state! Program is corrupted!")
	


# save data to file
# CAUTION: throw away the first sample
data = data[1:i, :]

data[:, 0] -= data[0, 0]

np.savetxt(fn, data, fmt='%.8f', delimiter=', ')

ser.close()

# plot

fig = plt.figure()

for j in range(12):

	ax = fig.add_subplot(12, 1, j + 1)

	ax.plot(data[:, 0], data[:, j + 1])


plt.show()


















