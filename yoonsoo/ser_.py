import pandas as pd
import numpy as np
import os
import shutil
import matplotlib.pyplot as plt
import librosa
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout, Average
from tensorflow.keras import regularizers
from tensorflow.keras import optimizers, Input, Model
#from keras.layers import LSTM
from tensorflow.keras.layers import Conv1D, MaxPooling1D
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
from tensorflow.keras.saving import save_model
from tensorflow.keras.metrics import CategoricalAccuracy

def extract_mfcc(filename):
	y, sr = librosa.load(filename, duration=3, offset=0.5)
	stft = np.abs(librosa.stft(y))
	result = np.array([])
	mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
	result = np.hstack((result, mfccs))
	chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sr).T,axis=0)
	result = np.hstack((result, chroma))
	mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T,axis=0)
	result = np.hstack((result, mel))
	return result



def train_model(modelname):
	X, y = load_data()

	'''
	model = Sequential([
		LSTM(256, return_sequences=False, input_shape=(X.shape[1],1)),
		Dropout(0.2),
		Dense(128, activation='relu'),
		Dropout(0.2),
		Dense(64, activation='relu'),
		Dropout(0.2),
		Dense(len(count), activation='softmax')
	])
	
	model = Sequential([
		Conv1D(256, 5,padding='same', input_shape=(X.shape[1],1), activation='relu'),
		Conv1D(128, 5,padding='same', activation='relu'),
		Dropout(0.1),
		MaxPooling1D(pool_size=(8)),
		Conv1D(128, 5,padding='same', activation='relu'),
		Conv1D(128, 5,padding='same', activation='relu'),
		Flatten(),
		Dense(len(count), activation='softmax')
	])
	'''
	model = Sequential([
		Conv1D(256, 5,padding='same', input_shape=(X.shape[1],1), activation='relu'),
		Conv1D(128, 5,padding='same', activation='relu', kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4)),
		Dropout(0.1),
		MaxPooling1D(pool_size=(8)),
		Conv1D(128, 5,padding='same', activation='relu', kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4)),
		Conv1D(128, 5,padding='same', activation='relu', kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4)),
		Dropout(0.5),
		Flatten(),
		Dense(len(count),
			kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4),
			bias_regularizer=regularizers.l2(1e-4),
			activity_regularizer=regularizers.l2(1e-5),
			activation='softmax'
		)
	])
	#'''
	epochs = 600
	model.compile(
		loss='categorical_crossentropy',
		optimizer=optimizers.Adam(1e-5),
		metrics=['accuracy']
	)
	model.summary()
	model_checkpoint_callback = ModelCheckpoint(
		filepath=modelname,
		monitor='val_accuracy',
		mode='max',
		save_best_only=True
	)
	history = model.fit(
		X, y, 
		validation_split=0.2, 
		epochs=epochs, 
		batch_size=16, 
		callbacks=[model_checkpoint_callback]
	)

	epochs = list(range(epochs))
	acc = history.history['accuracy']
	val_acc = history.history['val_accuracy']

	plt.plot(epochs, acc, label='train accuracy')
	plt.plot(epochs, val_acc, label='val accuracy')
	plt.xlabel('epochs')
	plt.ylabel('accuracy')
	plt.legend()
	plt.show()

	loss = history.history['loss']
	val_loss = history.history['val_loss']

	plt.plot(epochs, loss, label='train loss')
	plt.plot(epochs, val_loss, label='val loss')
	plt.xlabel('epochs')
	plt.ylabel('loss')
	plt.legend()
	plt.show()

def ensemble_model(modelnames, ensemblename): #ensemblename MUST be *.h5 !!
	models = []
	for name in modelnames:
		models.append(load_model(name, compile=False))
		models[-1].name = f'model{len(models)}'
	
	input_shape = models[0].layers[0]._build_shapes_dict['input_shape']
	input_shape.pop(0)
	input_shape = tuple(input_shape)
	model_input = Input(shape=input_shape)
	model_outputs = [model(model_input) for model in models]
	print(model_outputs)
	ensemble_output = Average()(model_outputs)
	ensemble_model = Model(inputs=model_input, outputs=ensemble_output)
	ensemble_model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizers.Adam(1e-5),
        metrics=['accuracy']
    )
	ensemble_model.save(ensemblename)
	ensemble_model = load_model(ensemblename)
	
	#ensemble_model.summary()
	X, y = load_data()
	a = ensemble_model.evaluate(X, y)


def test_model(modelname):
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

	model = load_model(modelname)
	if(input('press r to record new audio: ') == 'r'):
		record_sound()
	mfcc = extract_mfcc("temp.wav").reshape(1,-1)
	mfcc = np.expand_dims(mfcc, -1)
	label = ["angry","disgust","fear","happy","neutral","sad"]
	result = model.predict(mfcc)[0].tolist()
	print(dict(zip(label, result)))
	

if __name__ == '__main__':
	#organize_files()
	#train_model("./ser_model_crema_conv3.keras")
	test_model('ensemble.h5')
	'''
	ensemble_model(
		[
		"./ser_model_crema_conv.keras", 
		"./ser_model_crema_conv2.keras", 
		"./ser_model_crema_conv3.keras"
		],
		'ensemble.h5'
	)
	'''
