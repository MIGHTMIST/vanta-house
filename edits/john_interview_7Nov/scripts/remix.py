# 8 Nov: new sound only (owner: "fix the music and voices") - same picture, re-muxed. Music bed higher and continuous,
# room tone under every pause, softer voice joins (iv.render_audio fades 25/50 ms).
import sys, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv
S = iv.S
def mux(hq, wav):
    tmp = hq.replace('_HQ.mp4', '_HQ_new.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', hq, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-shortest', '-movflags', '+faststart', tmp], check=True)
    subprocess.run(['bash', S + '/scripts/fixtp.sh', tmp, hq], check=True); print(hq)
which = sys.argv[1]
if which == 'way1v':
    import way1v; P = way1v.build()
    a = iv.render_audio('way1v_r', P['voice'], P['sfx'], 'music_way1v_bed.mp3', P['dur'], music_db_under=14.0, smooth=True, lift=P['lifts'], lift_db=6.0)
    mux(S + '/out/John_Way1_FullInterview_MOOD_PLUS_9x16_1080_HQ.mp4', a)
if which == 'way3k':
    import way3k; P = way3k.build(1080, 1920)
    a = iv.render_audio('way3k_r', P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'], music_db_under=13.0, smooth=True, lift=P['lifts'], lift_db=7.0)
    mux(S + '/out/John_Way3_TrustFilm_MOOD_PLUS_9x16_1080_HQ.mp4', a)
