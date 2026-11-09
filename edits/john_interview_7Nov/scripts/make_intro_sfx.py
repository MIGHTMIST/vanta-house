#!/usr/bin/env python3
"""Synthesize intro SFX (phone vibrate/ring, keys, logo hit). 48k 16-bit stereo, peak -3 dBFS."""
import os, sys, wave
import numpy as np
from scipy import signal
SR = 48000
S = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("S", ".")
SND = os.path.join(S, "snd"); CHK = os.path.join(S, "out", "sfx_check")
os.makedirs(SND, exist_ok=True); os.makedirs(CHK, exist_ok=True)

def t_(n): return np.arange(int(n*SR))/SR
def bp(x, lo, hi, o=4): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def add(dst, src, at):
    i = int(round(at*SR)); n = max(0, min(len(src), len(dst)-i))
    if n > 0 and i >= 0: dst[i:i+n] += src[:n]
def ar(n, a, tau):  # fast attack, exponential decay
    t = np.arange(n)/SR
    return np.minimum(1, t/max(a, 1e-4)) * np.exp(-t/tau)
def pan(m, p):  # constant-power pan, p in -1..1
    a = (p+1)*np.pi/4; return np.stack([m*np.cos(a), m*np.sin(a)], 1)
def reverb_ir(rt, lpf=6000, seed=1, pre=0.012):
    r = np.random.default_rng(seed); n = int(rt*SR); t = np.arange(n)/SR
    out = []
    for _ in range(2):
        ir = r.standard_normal(n)*np.exp(-6.91*t/rt)
        ir = lp(ir, lpf); ir[:int(pre*SR)] = 0; ir /= np.sqrt((ir**2).sum()); out.append(ir)
    return np.stack(out, 1)
def reverb(x, ir, wet):  # x: (n,2) -> same length + tail
    L = signal.fftconvolve(x[:, 0], ir[:, 0]) + signal.fftconvolve(x[:, 1], ir[:, 1]*0.9)
    R = signal.fftconvolve(x[:, 1], ir[:, 1]) + signal.fftconvolve(x[:, 0], ir[:, 0]*0.9)
    wetsig = np.stack([L, R], 1)*0.7
    dry = np.pad(x, ((0, len(wetsig)-len(x)), (0, 0)))
    return dry + wet*wetsig
def finish(x, dur, name, fade_in=0.002, fade_out=0.05):
    n = int(dur*SR); x = x[:n] if len(x) >= n else np.pad(x, ((0, n-len(x)), (0, 0)))
    x = x - x.mean(0)
    x = np.stack([hp(x[:, c], 18, 2) for c in range(2)], 1)
    fi, fo = int(fade_in*SR), int(fade_out*SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]; x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    x *= 10**(-3/20)/np.abs(x).max()
    pcm = (np.clip(x, -1, 1)*32767).astype('<i2')
    with wave.open(os.path.join(SND, name), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return x

# ---------- 1. phone vibrate ----------
def make_vibrate():
    rng = np.random.default_rng(11); N = int(1.6*SR); mono = np.zeros(N); rat = np.zeros(N)
    for st in (0.12, 0.82):
        n = int(0.45*SR); t = np.arange(n)/SR
        f0 = 178 + 4*np.sin(2*np.pi*3.1*t)          # motor speed drifts slightly
        ph = 2*np.pi*np.cumsum(f0)/SR
        w = [1, .55, .38, .22, .15, .08]
        buzz = sum(a*np.sin((k+1)*ph + 0.4*k) for k, a in enumerate(w))
        buzz *= 1 + 0.18*np.sin(2*np.pi*23*t) + 0.07*np.sin(2*np.pi*7.3*t)
        env = np.minimum(1, t/0.03)**1.5 * np.minimum(1, (0.45-t)/0.06)
        buzz *= env
        # wooden desk rattle: band-passed noise gated by buzz cycles
        gate = np.clip(np.sin(ph) , 0, 1)**2 * (0.6+0.4*np.abs(np.sin(2*np.pi*31*t)))
        r = bp(rng.standard_normal(n), 900, 3800)*gate*env
        r += 0.5*bp(rng.standard_normal(n), 250, 700)*gate*env
        # case body resonance
        add(mono, buzz*0.8, st); add(rat, r*1.1, st)
    # desk contact thump at burst starts
    for st in (0.12, 0.82):
        n = int(0.06*SR); tt = np.arange(n)/SR
        add(rat, bp(rng.standard_normal(n), 400, 2500)*np.exp(-tt/0.01)*0.8, st)
    mono = lp(mono, 1800)
    x = pan(mono, -0.1) + pan(rat, 0.15)*0.55
    ir = reverb_ir(0.25, 4000, 3)
    x = reverb(x, ir, 0.12)
    return finish(x, 1.6, "sfx_phone_vibrate.wav", fade_out=0.08)

# ---------- 2. phone ring ----------
def bell(f, dur=0.9, tau=0.38, idx=2.2):
    n = int(dur*SR); t = np.arange(n)/SR
    env = np.minimum(1, t/0.004)*np.exp(-t/tau)
    modenv = np.exp(-t/0.09)
    m = np.sin(2*np.pi*f*3.0*t)*idx*modenv           # FM, ratio 3 -> bell/marimba
    y = np.sin(2*np.pi*f*t + m)*env
    y += 0.25*np.sin(2*np.pi*f*2*t)*np.exp(-t/0.2)   # marimba-ish 2nd partial
    y += 0.12*np.sin(2*np.pi*f*4.1*t)*np.exp(-t/0.05)  # woody strike
    return y
def make_ring():
    N = int(2.9*SR); x = np.zeros((N, 2))
    notes = [440.0, 554.37, 659.25, 739.99, 880.0]   # A4 C#5 E5 F#5 A5 (A maj pentatonic)
    for rep, st in enumerate((0.08, 1.25)):
        for k, f in enumerate(notes):
            lvl = 0.75 + 0.07*k + (0 if rep == 0 else -0.08)
            add_stereo = pan(bell(f)*lvl, -0.25 + 0.12*k)
            i = int(round((st+0.115*k)*SR)); x[i:i+len(add_stereo)] += add_stereo[:N-i]
    x = reverb(x, reverb_ir(0.9, 5500, 5), 0.28)
    return finish(x, 2.4, "sfx_phone_ring.wav", fade_out=0.25)

# ---------- 3/4. keys ----------
def key_mono(rng, kind="key", lvl=1.0, pitch=1.0, dur=0.12):
    n = int(dur*SR); y = np.zeros(n)
    heavy = kind in ("space", "enter")
    f_lo = (2000*pitch, 6000*pitch) if kind == "key" else (1500*pitch, 4500*pitch)
    cn = int(0.006*SR); t = np.arange(cn)/SR
    click = bp(rng.standard_normal(cn), f_lo[0], min(f_lo[1], 20000))*np.exp(-t/0.0015)
    y[:cn] += click*0.55*lvl
    f = {"key": 210, "space": 130, "enter": 150}[kind]*pitch
    tn = int({"key": 0.045, "space": 0.085, "enter": 0.07}[kind]*SR); tt = np.arange(tn)/SR
    thock = np.sin(2*np.pi*f*tt*(1+0.25*np.exp(-tt/0.01)))*np.exp(-tt/{"key": 0.014, "space": 0.03, "enter": 0.022}[kind])
    thock *= {"key": 0.8, "space": 1.15, "enter": 1.25}[kind]
    thock += 0.25*lp(rng.standard_normal(tn), 900)*np.exp(-tt/0.01)
    y[int(0.0008*SR):int(0.0008*SR)+tn] += thock[:n-int(0.0008*SR)]*lvl
    rel = int(0.07*SR) if not heavy else int(0.09*SR); rn = int(0.004*SR); rt = np.arange(rn)/SR
    if rel+rn < n:
        y[rel:rel+rn] += bp(rng.standard_normal(rn), 2500*pitch, 5500*pitch)*np.exp(-rt/0.0012)*0.22*lvl
    return y
def make_key_single():
    rng = np.random.default_rng(3)
    y = key_mono(rng, "key", 1.0, 1.0, 0.12)
    x = pan(y, 0.0) ; x = reverb(x, reverb_ir(0.12, 5000, 7), 0.08)
    return finish(x, 0.12, "sfx_key_single.wav", fade_out=0.02)
def make_typing():
    rng = np.random.default_rng(42); N = int(2.9*SR); x = np.zeros((N, 2))
    n_keys = 22
    iv = rng.uniform(0.07, 0.18, n_keys-1)
    # tune mean interval so the line lands ~2.35 s (stay within 70-180 ms)
    iv = np.clip(iv*(2.30/iv.sum()), 0.07, 0.18)
    times = 0.08 + np.concatenate([[0], np.cumsum(iv)])
    next_space = int(rng.integers(4, 8)); since = 0; kinds = []
    for i in range(n_keys):
        since += 1
        if i == n_keys-1: kinds.append("enter")
        elif since >= next_space and 0 < i < n_keys-2: kinds.append("space"); since = 0; next_space = int(rng.integers(4, 8))
        else: kinds.append("key")
    for i, (tm, kd) in enumerate(zip(times, kinds)):
        lvl = 10**(rng.uniform(-2, 2)/20)*(1.0 if kd != "enter" else 1.15)
        y = key_mono(rng, kd, lvl, rng.uniform(0.9, 1.1), 0.2 if kd != "key" else 0.14)
        s = pan(y, rng.uniform(-0.15, 0.15)); a = int(tm*SR); x[a:a+len(s)] += s[:N-a]
    x = reverb(x, reverb_ir(0.15, 5000, 8), 0.09)
    return finish(x, 2.6, "sfx_keys_typing.wav", fade_out=0.15), times, kinds

# ---------- 5. logo hit ----------
HIT = 0.30
def make_logo():
    rng = np.random.default_rng(21); N = int(4.0*SR); mono = np.zeros(N); sh = np.zeros(N)
    # sub boom: pitch drop 110 -> 50 Hz
    n = int(2.2*SR); t = np.arange(n)/SR
    f = 50 + 62*np.exp(-t/0.07)
    sub = np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1, t/0.004)*(np.exp(-t/0.75))
    sub += 0.35*np.sin(2*np.pi*np.cumsum(f*2)/SR)*np.exp(-t/0.2)
    body = lp(rng.standard_normal(n), 220)*np.exp(-t/0.12)*0.5      # soft thud
    air = bp(rng.standard_normal(n), 1200, 5000)*np.exp(-t/0.02)*0.12  # tiny transient
    add(mono, sub*1.0 + body + air, HIT)
    # shimmer: reverse swell lead-in (0.3 s) + soft decaying bloom after the hit
    ln = int(HIT*SR); lt = np.arange(ln)/SR
    nz = bp(rng.standard_normal(ln), 3500, 12000)
    lead = nz*(lt/HIT)**2.5*0.4
    bn = int(2.0*SR); bt = np.arange(bn)/SR
    bloom = bp(rng.standard_normal(bn), 3000, 11000)*np.exp(-bt/0.5)*0.12
    bloom += 0.1*sum(np.sin(2*np.pi*f0*bt+rng.uniform(0, 6))*np.exp(-bt/0.9) for f0 in (1760, 2217.5, 2637, 3520))
    add(sh, lead, 0.0); add(sh, bloom, HIT)
    x = pan(mono, 0) + np.stack([lp(sh, 11000), lp(np.roll(sh, 37), 11000)], 1)*0.6
    ir = reverb_ir(2.4, 3500, 9, 0.02)
    # reverb applied only to the post-start content; lead-in gets a little too
    x = reverb(x, ir, 0.38)
    return finish(x, 2.5, "sfx_logo_hit.wav", fade_out=0.45)

def stats(name, x):
    pk = 20*np.log10(np.abs(x).max()); rms = 20*np.log10(np.sqrt((x**2).mean()))
    print(f"{name}: {len(x)/SR:.3f}s peak {pk:.2f} dBFS rms {rms:.2f} dBFS dc {x.mean():.2e}")

def spec(name, x):
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    except Exception: return
    m = x.mean(1); fig, ax = plt.subplots(2, 1, figsize=(9, 5), sharex=True, gridspec_kw={'height_ratios': [1, 2]})
    ax[0].plot(np.arange(len(m))/SR, m, lw=.4); ax[0].set_ylim(-1, 1); ax[0].set_title(name)
    ax[1].specgram(m, NFFT=1024, Fs=SR, noverlap=768, cmap='magma', vmin=-130, vmax=-30); ax[1].set_ylim(0, 16000)
    ax[1].set_xlabel('s'); fig.tight_layout(); fig.savefig(os.path.join(CHK, name.replace('.wav', '.png')), dpi=90); plt.close(fig)

if __name__ == "__main__":
    ty, times, kinds = make_typing()
    outs = {"sfx_phone_vibrate.wav": make_vibrate(), "sfx_phone_ring.wav": make_ring(),
            "sfx_key_single.wav": make_key_single(), "sfx_keys_typing.wav": ty, "sfx_logo_hit.wav": make_logo()}
    for k, v in outs.items(): stats(k, v); spec(k, v)
    print("typing key times:", np.round(times, 3).tolist()); print("kinds:", "".join(k[0] for k in kinds))
    print("intervals ms:", np.round(np.diff(times)*1000).astype(int).tolist())
    print(f"logo hit point = {HIT:.3f} s ({int(HIT*SR)} samples)")
