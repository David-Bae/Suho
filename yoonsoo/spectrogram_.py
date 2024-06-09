import numpy as np
import matplotlib.pyplot as plt

def print_progress(event):
	from time import sleep
	from sys import stdout
	while not event.is_set():
		print('.', end='')
		stdout.flush()
		sleep(1)
	print('\nrecording stopped')
	stdout.flush()

def record_sound():
	import pyaudio
	from playsound import playsound
	import wave
	from threading import Thread, Event

	FORMAT = pyaudio.paInt16 # data type format
	CHANNELS = 2 # Adjust to your number of channels
	RATE = 44100 # Sample Rate
	CHUNK = 1024 # Block Size
	WAVE_OUTPUT_FILENAME = "temp.wav"

	audio = pyaudio.PyAudio()
	stream = audio.open(format=FORMAT, channels=CHANNELS,
				rate=RATE, input=True,
				frames_per_buffer=CHUNK)

	print("<ctrl-C to stop> recording:",end='')
	frames = []
	t1_stop = Event()
	t1 = Thread(target=print_progress, args=(t1_stop,))
	t1.start()
	
	try:	
		while True:
			data = stream.read(CHUNK)
			frames.append(data)
	
	except KeyboardInterrupt:
		t1_stop.set()
		stream.stop_stream()
		stream.close()
		audio.terminate()

	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()
	playsound(WAVE_OUTPUT_FILENAME)

if(input('press r to record new audio: ') == 'r'):
	record_sound()
'''
from scipy import signal
from scipy.io import wavfile

sample_rate, samples = wavfile.read('temp.wav')
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate, scaling='density')
	#len(spectogram) == len(frequencies),
	#len(spectogram[n]) == len(times)
#print(spectrogram[-1])
#print(times)
plt.pcolormesh(times, frequencies, np.log(spectrogram))
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()
'''

import parselmouth as pm

snd = pm.Sound('temp.wav')

def draw_spectrogram(spectrogram, dynamic_range=70):
	X, Y = spectrogram.x_grid(), spectrogram.y_grid()
	
	#wav value can be 0 in some cases, this raises runtime error in np.log10(div-by-0)
	#so convert all 0 to 1 -> log10(1) == 0
	spectrogram.values[spectrogram.values==0] = 1 #this takes some time to compute
	
	sg_db = 10 * np.log10(spectrogram.values)
	plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
	plt.ylim([spectrogram.ymin, spectrogram.ymax])
	plt.xlabel("time [s]")
	plt.ylabel("frequency [Hz]")

def draw_intensity(intensity):
	plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
	plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
	plt.grid(False)
	plt.ylim(0)
	plt.ylabel("intensity [dB]")

def draw_pitch(pitch):
	# Extract selected pitch contour, and
	# replace unvoiced samples by NaN to not plot
	pitch_values = pitch.selected_array['frequency']
	pitch_values[pitch_values==0] = np.nan
	#print(pitch_values)
	plt.plot(pitch.xs(), pitch_values, 'o', markersize=5, color='w')
	plt.plot(pitch.xs(), pitch_values, 'o', markersize=2)
	plt.grid(False)
	plt.ylim(0, pitch.ceiling)
	plt.ylabel("fundamental frequency [Hz]")

def detect_question(pitch, intensity):
	
	thres = 60 #intensity threshold (dB)
	dfdt = 300 #pitch delta threshold (Hz)
	mintime = 9 #minimum segment length (0.01x sec)

	i, length = 0, 0
	first, last = None, None
	low, high = None, None
	pitch_values = pitch.selected_array['frequency']
	intensity_values = intensity.values.T
	
	while i < len(pitch_values):
		
		try:
			while pitch_values[i] == 0 or intensity_values[i] < thres:
				i += 1
			
			first = i #found first point of potential segment
			low = {'index':i, 'value':pitch_values[i]} #set first point as lowest
			
			while pitch_values[i] != 0 and intensity_values[i] >= thres:
				i += 1
				if pitch_values[i] != 0 and pitch_values[i] < low['value']: #update 'low' point
					low['index'] = i
					low['value'] = pitch_values[i]
			last = i #segment ends,
			         #but segment may be only temporarily severed
			
			length = last - first + 1 #use heat-based gap mitigation in respect to length
			while length > 0 and intensity_values[i] >= thres: #however, intensity should be above thres
				i += 1
				if pitch_values[i] == 0:
					length -= 10 #ignore gaps proportional to segment length
					continue
				last = i
				length += 1

			high = {'index':i, 'value':low['value']}
			for i in range(low['index'], last+1):  #from 'low' point until last point of audio segment
				if pitch_values[i] > high['value']: #search for 'high' point
					high['index'] = i
					high['value'] = pitch_values[i]

		except IndexError:
			break
		
		length = last - first
		if length < mintime: #if pitch segment is too short (<0.09s)
			length = 0  #reset length
			continue    #restart search
		break
	
	v_first = pitch_values[first]
	v_last = pitch_values[last]
	v_low = low['value']
	v_high = high['value']

	dt = 0
	if length >= mintime:
		pitch_times = pitch.xs()
		t_first = pitch_times[first]
		t_last = pitch_times[last]
		t_low = pitch_times[low['index']]
		t_high = pitch_times[high['index']]
		
		df = v_high - v_low
		dt = t_high - t_low

		print(f'df = {df}')
		if dt != 0: print(f'df/dt = {df/(t_high-t_low)}')

	return (False, None) if length == 0 else True, (False if dt == 0 else df/dt > dfdt)
	#returns (False, None) if no proper pitch sequence found
	#returns (True, True/False) if sequence is found and is/isn't question tone


intensity = snd.to_intensity(time_step=0.01)
pitch = snd.to_pitch(time_step=0.01)
found, is_question = detect_question(pitch, intensity)
print(f'found:{found}, is_question:{is_question}')
