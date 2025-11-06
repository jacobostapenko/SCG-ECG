import os
import wfdb
import numpy as np
import h5py
from scipy.signal import butter, filtfilt



data_dir = "/Users/jacobostapenko/Desktop/CEBSDB"
RECORDS = [os.path.splitext(f)[0] for f in os.listdir(data_dir) if f.endswith('.hea')]
OUT_DIR = "/Users/jacobostapenko/Desktop/CEBSDB/processed"
os.makedirs(OUT_DIR, exist_ok=True)

ECG_BAND = (5, 40)      # Hz
SCG_BAND = (0.8, 25)    # Hz
BPF_ORDER = 2           # Butterworth order


def bandpass(sig, low, high, fs, order=BPF_ORDER):
    b, a = butter(order, [low, high], btype='bandpass', fs=fs)
    return filtfilt(b, a, sig)


def process_record(record_path, out_dir=OUT_DIR):
    record_name = os.path.basename(record_path)
    h5_file = os.path.join(out_dir, f"{record_name}.h5")
    
    # Skip if already processed
    if os.path.exists(h5_file):
        print(f"{record_name} already processed. Skipping.")
        return
        
    record = wfdb.rdrecord(record_path)
    fs = record.fs
    sigs = record.p_signal
    channels = record.sig_name
    
    # Identify ECG and SCG channels
    try:
        ecg_idx = channels.index("II")
    except ValueError:
        raise ValueError(f"ECG channel not found in {record_name}")
    try:
        scg_idx = channels.index("SCG")  # or SCG2 depending on preference
    except ValueError:
        raise ValueError(f"SCG channel not found in {record_name}")
    
    ecg = sigs[:, ecg_idx]
    scg = sigs[:, scg_idx]
    

    ann = wfdb.rdann(record_path, 'atr')
    first_annotation = ann.sample[0]  # first annotation as reference
    
    # Align signals based on first annotation
    ecg = ecg[first_annotation:]
    scg = scg[first_annotation:]

    min_len = min(len(ecg), len(scg))
    ecg = ecg[:min_len]
    scg = scg[:min_len]
    
    
    ecg_filt = bandpass(ecg, ECG_BAND[0], ECG_BAND[1], fs)
    scg_filt = bandpass(scg, SCG_BAND[0], SCG_BAND[1], fs)
    
    # # Optional SCG preprocessing
    # scg_filt = scg_filt - np.mean(scg_filt)        # detrend
    # scg_filt = scg_filt / np.std(scg_filt)         # normalize
    

    with h5py.File(h5_file, "w") as f:
        f.create_dataset("ECG", data=ecg_filt)
        f.create_dataset("SCG", data=scg_filt)
        f.attrs["fs"] = fs
        f.attrs["ECG_band"] = ECG_BAND
        f.attrs["SCG_band"] = SCG_BAND
        # Save first few annotation samples for reference
        f.create_dataset("annotations", data=ann.sample[:10])
    
    print(f"{record_name} saved to {h5_file}")


if __name__ == "__main__":
    # Discover all records (without extension)
    
    for rec in RECORDS:
        record_path = os.path.join(data_dir, rec)
        process_record(record_path)
