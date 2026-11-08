import json
v=json.load(open('team24_verified_draft.json'))
p=json.load(open('team24_pending_draft.json'))
leads=[
 {"url":"https://app.grupodewhatsapp.com/","source":"grupodewhatsapp"},
 {"url":"https://app.grupodewhatsapp.com/categorias","source":"grupodewhatsapp-cats"},
 {"url":"https://app.grupodewhatsapp.com/amizade","source":"grupodewhatsapp-amizade"},
 {"url":"https://app.grupodewhatsapp.com/emprego","source":"grupodewhatsapp-emprego"},
 {"url":"https://app.grupodewhatsapp.com/esportes","source":"grupodewhatsapp-esportes"},
 {"url":"https://app.grupodewhatsapp.com/estudos","source":"grupodewhatsapp-estudos"},
 {"url":"https://app.grupodewhatsapp.com/musica","source":"grupodewhatsapp-musica"},
 {"url":"https://app.grupodewhatsapp.com/series-e-filmes","source":"grupodewhatsapp-series-filmes"},
 {"url":"https://app.grupodewhatsapp.com/juegos","source":"grupodewhatsapp-juegos"},
 {"url":"https://app.grupodewhatsapp.com/amor-e-romance","source":"grupodewhatsapp-amor"},
 {"url":"https://app.grupodewhatsapp.com/anime","source":"grupodewhatsapp-anime"},
 {"url":"https://app.grupodewhatsapp.com/concursos","source":"grupodewhatsapp-concursos"},
 {"url":"https://gruposdewhatss.app/","source":"gruposdewhatss"},
 {"url":"https://frilajobs.com.br/grupos/","source":"frilajobs"},
 {"url":"https://whatshub.es/trends","source":"whatshub"},
 {"url":"https://www.gruposwats.com/","source":"gruposwats"},
 {"url":"https://linkado.app/?page=7","source":"linkado-p7"},
 {"url":"https://www.droiders.com/enlaces-grupos-whatsapp-para-unirse/","source":"droiders-roundup"},
]
outdir='..'
def w(name, data):
    for attempt in range(5):
        try:
            with open(f'{outdir}/{name}','w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=1)
            print('wrote',name,len(data)); return
        except Exception as e:
            print('write retry',name,e)
    raise SystemExit(f'FAILED to write {name}')
w('team24-latam-brazil.json', v)
w('team24-latam-brazil-pending.json', p)
w('team24-latam-brazil-leads.json', leads)
