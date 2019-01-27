#!/usr/bin/env python3
import sys,psutil,os
from ADCDACPi import ADCDACPi
import time
import RPi.GPIO as GPIO
import soundfile as sf
from pysndfx import AudioEffectsChain


p = psutil.Process(os.getpid())
p.nice(10)

fx = (
    AudioEffectsChain()
    #.highshelf()
    #.reverb()
    #.phaser()
    .delay(0.8,0.8 ,(150,180),(0.3,0.25))
    .lowpass(12000,0.707)
)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, False)

adcdac = ADCDACPi(2)
normalized=[]
normalized_nofx = []
normalized_fx = []
Enc_A = 11  
Enc_B = 13
Button = 15
vol=5
dsp=0

filename = sys.argv[1] if len(sys.argv) > 1 else 'mario.raw'

data, samplerate = sf.read(filename , channels=1, samplerate=12500,
                           subtype='PCM_U8') #8bit Samples
                           #subtype='PCM_16') #for 12bit encoded as 16bit
def init():
    global data
    global data_fx
    print ("DAC sound player Test Program")
    print ("File for playback :"+ filename)
    print ("Loading sound file.")

    print ("Applying sound fx.")
    data_fx=fx(data)
    GPIO.setwarnings(True)
    #GPIO.setmode(GPIO.BCM)
    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)
    GPIO.setup(Button, GPIO.IN)
    GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotation_decode, bouncetime=50)
    GPIO.add_event_detect(Button, GPIO.RISING, callback=button_press, bouncetime=50)
    return

def rotation_decode(Enc_A):
    global counter
    global vol
    #time.sleep(0.002)
    Switch_A = GPIO.input(Enc_A)
    Switch_B = GPIO.input(Enc_B)
 
    if (Switch_A == 1) and (Switch_B == 0):
        #counter += 1
        vol=vol-0.25
        while Switch_B == 0:
            Switch_B = GPIO.input(Enc_B)
        while Switch_B == 1:
            Switch_B = GPIO.input(Enc_B)
        return
 
    elif (Switch_A == 1) and (Switch_B == 1):
        #counter -= 1
        vol=vol+0.25
        while Switch_A == 1:
            Switch_A = GPIO.input(Enc_A)
        return
    else:
        return
def button_press(button):
    global dsp
    global normalized
    global normalized_fx
    global normalized_nofx
    if dsp==0 :
        normalized=normalized_fx
        dsp=1
        print ("Sound effects active. ")
    else:
        normalized=normalized_nofx
        dsp=0
        print ("Sound effects disabled. ")    
    return
   
def main():
    global data
    global normalized
    global normalized_nofx
    global normalized_fx
    try:
         init()
        #while True :
        #    sleep(1)
         print ("Normalizing...")
         for y in data:
            normalized_nofx.append(abs((y-1)/(255-1)))
            #print(y)
            normalized=normalized_nofx
         print ("Normalizing done..:")
         print ("Normalizing sound effects...")
         for y in data_fx:
            normalized_fx.append(abs((y-1)/(255-1)))
         print ("Normalizing done..:")

         #del data
         print ("Starting playback..:")
         timestart=time.time()
         for x in range(0, len(normalized)):
            #print (normalized[x])
            #print ("Normalized:" + str(normalized[x]))
            adcdac.set_dac_voltage(1, normalized[x]*vol)
         #  adcdac.set_dac_voltage(1, 0)
         tfs = len(normalized) / (time.time() - timestart)
         print ("Sampling rate achieved:" + str(int(tfs)))
        
 
    except KeyboardInterrupt:
        GPIO.cleanup()
 
if __name__ == '__main__':
    main()


