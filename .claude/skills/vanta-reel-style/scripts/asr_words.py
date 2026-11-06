import sys, json, numpy as np, soundfile as sf, sherpa_onnx
D='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{D}/encoder.int8.onnx',decoder=f'{D}/decoder.int8.onnx',joiner=f'{D}/joiner.int8.onnx',tokens=f'{D}/tokens.txt',model_type='nemo_transducer',num_threads=4)
x,sr=sf.read(sys.argv[1],dtype='float32'); x=x.mean(1) if x.ndim>1 else x
t0=float(sys.argv[3]) if len(sys.argv)>3 else 0; t1=float(sys.argv[4]) if len(sys.argv)>4 else len(x)/sr
seg=x[int(t0*sr):int(t1*sr)]
st=rec.create_stream(); st.accept_waveform(sr,seg); rec.decode_stream(st)
r=st.result; toks=r.tokens; ts=r.timestamps
words=[]
for tk,t in zip(toks,ts):
    if tk.startswith(' ') or tk.startswith('▁') or not words:
        words.append({'w':tk.strip(' ▁'),'t':round(t+t0,3)})
    else: words[-1]['w']+=tk
for i,w in enumerate(words): w['end']=round(words[i+1]['t'] if i+1<len(words) else t1,3)
json.dump({'text':r.text,'words':words},open(sys.argv[2],'w'),indent=0)
print(r.text); print(len(words),'words')
