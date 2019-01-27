#!/usr/bin/env python
from ADCDACPi import ADCDACPi
import time
import matplotlib.pyplot as plt
from matplotlib.mlab import find
from numpy.fft import rfft
from numpy import argmax, mean, diff, log
from scipy.signal import blackmanharris, fftconvolve

def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.
   
    f is a vector and x is an index for that vector.
   
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
   
    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.
   
    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
   
    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
   
    """
    # Requires real division.  Insert float() somewhere to force it?
    xv = 1/2 * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4 * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)

def freq_from_crossings(sig, fs):
    """
    Estimate frequency from peak of FFT
    """
    # Compute Fourier transform of windowed signal
    windowed = sig * blackmanharris(len(sig))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f))  # Just use this for less-accurate, naive version
    true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)

def freq_from_fft(sig, fs):
    """
    Estimate frequency from peak of FFT
    """
    # Compute Fourier transform of windowed signal
    windowed = sig * blackmanharris(len(sig))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f))  # Just use this for less-accurate, naive version
    true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)


adcdac = ADCDACPi(1)
adcdac.set_adc_refvoltage(3.3)
valuesx = []
valuesy = []
tmp = []
timestart=time.time()
for x in range(0, 10000):
   valuesx.append(adcdac.read_adc_voltage(1, 0))
   #time.sleep(0.0001)
   timenow =  time.time() - timestart
   valuesy.append(timenow)

tfs = 10000 / (time.time() - timestart)
for val in valuesx:
    tmp.append(val-1.7)

print ("Samples Per Second:" + str(tfs))
#print (valuesy)
print ("Freq:"+ str(freq_from_fft(tmp, tfs)))
plt.plot(valuesy,valuesx)
plt.show()

