import scipy
import matplotlib.pyplot as plt
import h5py
import os 
import numpy as np

def visualize_signal(signal, fs):    
    time = np.arange(len(signal)) / fs
    plt.figure(figsize=(12, 4))
    plt.plot(time, signal)
    
    # Calculate ticks every 30 seconds
    tick_interval = 60 * fs
    xticks = np.arange(0, len(signal), tick_interval)
    xtick_labels = (xticks / fs).astype(int)  # Convert to seconds
    
    plt.xticks(xticks / fs, xtick_labels, rotation=45)  # Align ticks with time axis
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Signal Visualization')
    plt.grid()
    plt.show()


def extract_cardiac_features(scg_signal):
    #

def process():
    file_dir = "/Users/jacobostapenko/Desktop/CEBSDB/processed"
    for h5_file in os.listdir(file_dir):
        if h5_file.endswith('.h5'):
            full_path = os.path.join(file_dir, h5_file)
            with h5py.File(full_path, 'r') as f:
                fs = f.attrs['fs']
                ecg = f['ECG'][:]
                scg = f['SCG'][:]
                
                print(f"Visualizing ECG from {h5_file}")
                visualize_signal(ecg, fs)
                
                print(f"Visualizing SCG from {h5_file}")
                visualize_signal(scg, fs)

process()