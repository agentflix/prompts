import sys,glob,re,numpy as np
from PIL import Image
def db(y): return -12-(y-91)*6/8
def series(d, x0=676, x1=686):
    out=[]
    for f in sorted(glob.glob(d+'/w*.png')):
        t=int(re.search(r'_(\d+)\.png',f).group(1))/1000
        im=np.array(Image.open(f).convert('RGB')).astype(int)
        sat=(im.max(2)-im.min(2))>22
        band=sat[77:326,x0:x1].any(1)          # linhas com cor
        if not band.any(): out.append((t,None,None)); continue
        ys=np.where(band)[0]+77
        top=ys[0]
        # curva = run contígua que chega ao fundo
        y=325
        while y>77 and band[y-77]: y-=1
        cur=y+1
        out.append((t,db(cur),db(top)))
    return out
if __name__=='__main__':
    for t,c,p in series(sys.argv[1])[::int(sys.argv[2]) if len(sys.argv)>2 else 1]:
        print(f'{t:6.3f} curva={c if c is None else round(c,1)} pico={p if p is None else round(p,1)}')
