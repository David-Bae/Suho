import numpy as np
import librosa
from tensorflow.keras.models import load_model

def extract_mfcc(filename):
    y, sr = librosa.load(filename, duration=3, offset=0.5)
    stft = np.abs(librosa.stft(y))
    result = np.array([])
    mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    result = np.hstack((result, mfccs))
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sr).T, axis=0)
    result = np.hstack((result, chroma))
    mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
    result = np.hstack((result, mel))
    return result

def SER(mp3_path):
    model = load_model("/usr/src/apps/utils/models/ser_ensemble.h5")
    mfcc = extract_mfcc(mp3_path).reshape(1, -1)
    mfcc = np.expand_dims(mfcc, -1)
    label = ["angry", "disgust", "fear", "happy", "neutral", "sad"]
    result = model.predict(mfcc)[0].tolist()
    max_index = result.index(max(result))
    
    return max_index