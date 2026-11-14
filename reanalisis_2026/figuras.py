import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
OUT=sys.argv[1]
r=json.load(open(f'{OUT}/metricas_por_zona.json')); p=json.load(open(f'{OUT}/paletas_K6_umbral15.json'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
# Figura 1: máscaras
cols={1:(0.85,0.2,0.2),2:(0.2,0.6,0.2),3:(0.2,0.35,0.85),9:(0,0,0)}
fig,ax=plt.subplots(1,2,figsize=(10,6.6))
for i,k in enumerate('AB'):
    im=np.asarray(Image.open(f'{OUT}/lienzo_{k}_balanceado.png')).astype(float)/255; z=np.load(f'{OUT}/zonas_{k}.npy')
    for c,v in cols.items(): m=z==c; im[m]=0.55*im[m]+0.45*np.array(v)
    ax[i].imshow(im); ax[i].set_title(f'Lienzo {k}: zonas propuestas'); ax[i].axis('off')
fig.legend(handles=[Patch(color=cols[1],label='Figura'),Patch(color=cols[2],label='Elementos asociados'),Patch(color=cols[3],label='Texto'),Patch(color=(0.9,0.9,0.9),label='Resto del lienzo'),Patch(color='k',label='Excluido (clip)')],loc='lower center',ncol=5,frameon=False)
plt.tight_layout(rect=(0,0.05,1,1)); plt.savefig(f'{OUT}/F1_mascaras_propuestas.png',dpi=150); plt.close()
# Figura 2: paletas de la figura y familias de tono
fams=["rojo","naranja","amarillo","verde","azul","violeta","rosa/magenta","marrón"]
famcol={"rojo":"#B03A2E","naranja":"#D9822B","amarillo":"#D4C21A","verde":"#4E9A3A","azul":"#2F4FA2","violeta":"#7B4FA0","rosa/magenta":"#B04A7A","marrón":"#7A5537"}
fig,ax=plt.subplots(2,2,figsize=(10,5.6),gridspec_kw={'height_ratios':[1,1.3]})
for i,k in enumerate('AB'):
    pal=p[f'{k}_figura']; a=ax[0,i]; x=0
    for hx,pct,C in pal:
        a.barh(0,pct,left=x,color=hx,edgecolor='white'); 
        if pct>6: a.text(x+pct/2,0,f'{hx}\n{pct:.1f} %',ha='center',va='center',color='white' if sum(int(hx[j:j+2],16) for j in (1,3,5))<380 else 'black',fontsize=7)
        x+=pct
    a.set_xlim(0,100); a.set_yticks([]); a.set_xlabel('% de píxeles con color de la figura'); a.set_title(f'Lienzo {k}: paleta de la figura (CIELAB, K = 6, C* ≥ 15)')
    for s in ('top','right','left'): a.spines[s].set_visible(False)
    e=r[k]['zonas']['figura']['por_umbral']['15']; f=e['familias']
    b=ax[1,i]; vals=[100*f[n] for n in fams]
    b.bar(range(len(fams)),vals,color=[famcol[n] for n in fams]); b.set_xticks(range(len(fams))); b.set_xticklabels(fams,rotation=30,ha='right'); b.set_ylim(0,70); b.set_ylabel('% de píxeles con color')
    for j,v in enumerate(vals):
        if v>=1: b.text(j,v+1,f'{v:.0f}',ha='center',fontsize=8)
    b.set_title(f'Familias de tono · sin color: {100*e["prop_sin_color"]:.0f} % · croma (con color): {e["croma_media_coloreados"]:.1f}',fontsize=8.5)
    for s in ('top','right'): b.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(f'{OUT}/F2_figura_paleta_y_familias.png',dpi=150); plt.close()
print('ok')
