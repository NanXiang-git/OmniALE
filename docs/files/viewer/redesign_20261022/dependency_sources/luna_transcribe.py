import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, find_peaks
from scipy.ndimage import median_filter, maximum_filter1d

sr,x=wavfile.read('/tmp/piano.wav')
x=x.astype(np.float32)/32768
# Harmonic spectral templates with whitening reduce masking by piano fundamentals.
f,t,Z=stft(x,fs=sr,nperseg=4096,noverlap=4096-220,boundary='zeros')
V=np.abs(Z).astype(np.float32)
midis=np.arange(33,96)
freq=440*2**((midis-69)/12)
templates=np.zeros((len(f),len(midis)),np.float32)
for j,ff in enumerate(freq):
    for h in range(1,9):
        hz=ff*h
        if hz>=sr/2: break
        idx=hz/(sr/4096)
        k=int(round(idx))
        if 1<=k<len(f)-1:
            templates[k-1:k+2,j]+=np.array([.2,1,.2],np.float32)/(h**1.25)
weight=1/np.maximum(np.mean(V,axis=1),1e-5)**.65
A=templates*weight[:,None]
A/=np.maximum(np.linalg.norm(A,axis=0),1e-8)
B=V*weight[:,None]
# Nonnegative multiplicative updates, sparse penalty suppresses harmonic ghosts.
AtA=A.T@A; AtB=A.T@B
H=np.maximum(AtB,1e-7)
for _ in range(28): H*=np.maximum(AtB-.06,1e-8)/(AtA@H+1e-8)
H=median_filter(H,size=(1,3))
events=[]
for j,m in enumerate(midis):
    a=H[j]
    # Relative floor plus local prominence to retain rearticulations.
    th=max(a.max()*.20, np.percentile(a,80)*1.8)
    active=a>th
    # bridge gaps <= 30 ms
    for k in range(1,4):
        active[ k:-k] |= active[:-2*k] & active[2*k:]
    edges=np.diff(np.r_[0,active,0].astype(int))
    starts=np.where(edges==1)[0]; ends=np.where(edges==-1)[0]
    for s,e in zip(starts,ends):
        if e-s<8: continue
        # split clear attacks inside sustained activation
        seg=a[s:e]
        peaks,_=find_peaks(seg,distance=12,prominence=max(a.max()*.14,.08))
        cuts=[s]
        for p in peaks:
            p+=s
            if p-s>10 and e-p>10 and a[p]>a[s:p].max()*1.35: cuts.append(p)
        cuts.append(e)
        for u,v in zip(cuts,cuts[1:]):
            if v-u>=8: events.append((max(0,t[u]),int(m),max(.09,t[v-1]-t[u])))
events.sort()
np.savetxt('/tmp/events.csv',np.array(events),delimiter=',',fmt=['%.3f','%d','%.3f'],header='time,midi,duration',comments='')
print('events',len(events),'range',events[:10],events[-10:])
