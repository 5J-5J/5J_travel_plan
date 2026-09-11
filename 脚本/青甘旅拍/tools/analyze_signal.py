"""Measure MP3 energy and periodicity with NumPy. This is not a listening review."""
from pathlib import Path
import json
import importlib.metadata
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tmp" / "audio_packages"))
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

source = PROJECT.parents[1] / "bgm" / "dc39D5yN-Places-Portair.mp3"
out = PROJECT / "analysis"
out.mkdir(exist_ok=True)
audio, sr = sf.read(source, dtype="float32", always_2d=True)
mono = audio.mean(axis=1)
duration = len(audio) / sr
hop = 1024
size = 2048
pad = np.pad(mono, (size//2, size//2))
frames = np.lib.stride_tricks.sliding_window_view(pad, size)[::hop]
rms = np.sqrt(np.mean(frames**2, axis=1))
spec = np.abs(np.fft.rfft(frames * np.hanning(size), axis=1))
freq = np.fft.rfftfreq(size, 1/sr)
centroid = (spec * freq).sum(axis=1) / np.maximum(spec.sum(axis=1), 1e-10)
logspec = np.log1p(spec)
flux = np.maximum(np.diff(logspec, axis=0), 0).mean(axis=1)
flux = np.r_[0, flux]
times = np.arange(len(rms))*hop/sr
centered = flux - flux.mean()
fsize = 1 << (2*len(centered)-1).bit_length()
fft = np.fft.rfft(centered, n=fsize)
autocorr = np.fft.irfft(fft*np.conj(fft), n=fsize)[:len(centered)]
autocorr /= np.arange(len(centered),0,-1)
lo, hi = int(60/180*sr/hop), int(60/55*sr/hop)
lags = [i for i in range(lo+1,hi) if autocorr[i]>autocorr[i-1] and autocorr[i]>=autocorr[i+1]]
lags.sort(key=lambda i:autocorr[i], reverse=True)
tempo_candidates = [{"bpm":round(60*sr/hop/i,3),"lag_frames":i,"relative_score":round(float(autocorr[i]/max(autocorr[0],1e-12)),4)} for i in lags[:5]]
peaks = [i for i in range(1,len(flux)-1) if flux[i]>flux[i-1] and flux[i]>=flux[i+1] and flux[i]>np.percentile(flux,65)]
bins=[]
for start in np.arange(0,duration,4):
    end=min(float(start+4),duration)
    mask=(times>=start)&(times<end)
    bins.append({"start_s":float(start),"end_s":round(end,3),
                 "rms_dbfs_mono":round(float(20*np.log10(max(np.sqrt(np.mean(rms[mask]**2)),1e-10))),2),
                 "centroid_hz":round(float(np.mean(centroid[mask])),1),
                 "positive_spectral_flux":round(float(np.mean(flux[mask])),5)})
result={
    "source_file":"bgm/"+source.name,"decoded_duration_s":duration,"sample_rate_hz":sr,"channels":audio.shape[1],
    "tempo_candidates":tempo_candidates,"tempo_status":"Periodicity candidates only, not confirmed tempo or downbeats. No beat grid is claimed.",
    "transient_candidates_s":[round(float(times[i]),6) for i in peaks],
    "four_second_windows":bins,
    "method":"soundfile decode; 2048-sample Hann FFT / 1024 hop; mono RMS, centroid, positive log spectral flux; flux autocorrelation",
    "listening_status":"No aural review; no lyric, instrument, chorus, or emotional observations claimed.",
    "packages":{x:importlib.metadata.version(x) for x in ["numpy","soundfile","pillow"]}}
(out/"audio_structure.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
(PROJECT/"tools"/"requirements_audio.txt").write_text("\n".join(k+"=="+v for k,v in result['packages'].items())+"\n",encoding="utf-8")
np.savez_compressed(PROJECT/"tmp"/"audio_features.npz",times=times,rms=rms,flux=flux,centroid=centroid)
im=Image.new("RGB",(2000,950),"#101826")
d=ImageDraw.Draw(im)
font_path="C:/Windows/Fonts/arial.ttf"
font=lambda n:ImageFont.truetype(font_path,n)
d.text((80,35),"PLACES / PORTAIR",font=font(32),fill="white")
d.text((80,82),"Measured energy and transients - original source seconds - not an aural review",font=font(21),fill="#a7bccb")
x0,x1=100,1935
panels=[(160,350,"Waveform",-1,1,"#64d8c9"),(430,610,"RMS / dBFS",-50,0,"#f0b879"),(690,860,"Positive spectral flux",0,float(np.percentile(flux,99.5)),"#acb7ff")]
for top,bottom,label,vmin,vmax,color in panels:
    d.text((x0,top-34),label,font=font(20),fill=color)
    for sec in range(0,int(duration)+1,10):
        x=x0+(x1-x0)*sec/duration
        d.line((x,top,x,bottom),fill="#263746")
        d.text((x-8,bottom+6),str(sec),font=font(14),fill="#c1cfda")
    for frac in [0,.5,1]:
        yy=bottom-frac*(bottom-top)
        d.line((x0,yy,x1,yy),fill="#304251")
    if label=='Waveform':
        for pixel in range(x1-x0):
            a=int(pixel/(x1-x0)*len(mono)); b=max(a+1,int((pixel+1)/(x1-x0)*len(mono)))
            low,high=float(mono[a:b].min()),float(mono[a:b].max())
            yy=lambda v:bottom-(v-vmin)/(vmax-vmin)*(bottom-top)
            d.line((x0+pixel,yy(low),x0+pixel,yy(high)),fill=color)
    else:
        vals=20*np.log10(np.maximum(rms,1e-8)) if label.startswith('RMS') else flux
        pts=[(x0+(x1-x0)*float(t)/duration,bottom-(min(max(float(v),vmin),vmax)-vmin)/(vmax-vmin)*(bottom-top)) for t,v in zip(times[::3],vals[::3]) if t<=duration]
        d.line(pts,fill=color,width=2)
im.save(out/"audio_structure.png")
print(json.dumps({k:v for k,v in result.items() if k not in ('transient_candidates_s','four_second_windows')},indent=2))
for row in bins:print(row)
