import matplotlib.pyplot as plt
import numpy
import scipy.io.wavfile
from scipy.fftpack import dct
import sys

def printa(signal, figure_name):
    plt.figure(1)
    plt.title(figure_name)
    plt.plot(signal)
    plt.show()

def pre_emphasis(signal):
    alpha = 0.95
    emphasized_signal = numpy.append(signal[0], signal[1:] - alpha * signal[:-1])
    return emphasized_signal

def framing(emphasized_signal, sample_rate):
    frame_size = 0.025
    frame_stride = 0.01
    frame_length, frame_step = frame_size * sample_rate, frame_stride * sample_rate  # Convert from seconds to samples
    signal_length = len(emphasized_signal)
    frame_length = int(round(frame_length))
    frame_step = int(round(frame_step))
    num_frames = int(numpy.ceil(float(numpy.abs(signal_length - frame_length)) / frame_step))  # Make sure that we have at least 1 frame

    pad_signal_length = num_frames * frame_step + frame_length
    z = numpy.zeros((pad_signal_length - signal_length))
    pad_signal = numpy.append(emphasized_signal, z) # Pad Signal to make sure that all frames have equal number of samples without truncating any samples from the original signal

    indices = numpy.tile(numpy.arange(0, frame_length), (num_frames, 1)) + numpy.tile(numpy.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(numpy.int32, copy=False)]

    return frames

def hamming(frames):
    frames *= numpy.hamming(len(frames[0]))
    return frames

def periodogram(frames):
    NFFT = 512
    mag_frames = numpy.absolute(numpy.fft.rfft(frames, NFFT))  # Magnitude of the FFT
    pow_frames = ((1.0 / NFFT) * ((mag_frames) ** 2))  # Power Spectrum
    return pow_frames

def filter_bank(pow_frames, sample_rate):
    NFFT = 512
    nfilt = 40
    low_freq_mel = 0
    high_freq_mel = (2595 * numpy.log10(1 + (sample_rate / 2) / 700))  # Convert Hz to Mel
    mel_points = numpy.linspace(low_freq_mel, high_freq_mel, nfilt + 2)  # Equally spaced in Mel scale
    hz_points = (700 * (10**(mel_points / 2595) - 1))  # Convert Mel to Hz
    bin = numpy.floor((NFFT + 1) * hz_points / sample_rate)

    fbank = numpy.zeros((nfilt, int(numpy.floor(NFFT / 2 + 1))))
    for m in range(1, nfilt + 1):
        f_m_minus = int(bin[m - 1])   # left
        f_m = int(bin[m])             # center
        f_m_plus = int(bin[m + 1])    # right

        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
    filter_banks = numpy.dot(pow_frames, fbank.T)
    filter_banks = numpy.where(filter_banks == 0, numpy.finfo(float).eps, filter_banks)  # Numerical Stability
    filter_banks = 20 * numpy.log10(filter_banks)  # dB

    return filter_banks


def main():
    sample_rate, signal = scipy.io.wavfile.read('00001outro.wav')
    signal = signal[0:int(2 * sample_rate)]

    #printa(signal, "Original Signal")

    emphasized_signal = pre_emphasis(signal)

    #printa(emphasized_signal, "Emphatized Signal")

    frames = framing(emphasized_signal, sample_rate)
    
    #printa(frames, "FRAMEZAO")

    ham = hamming(frames)

    #printa (ham, "HAMZAO")

    period = periodogram(frames)

    #printa(period, "PERIODOZAO")

    filtrado = filter_bank(period, sample_rate)
    plot_fbank(filtrado)
    #printa(filtrado, "FILTRADAO")


if __name__ == "__main__":
  sys.exit(main())