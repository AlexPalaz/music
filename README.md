# alexpalaz-music-links — smart link di Alex Palaz

Un sito statico, gratuito, con una pagina per ogni uscita e la home che le elenca.
Ogni pagina ha il Pixel Meta e traccia i click verso le piattaforme (evento `Lead`).

## Aggiungere un'uscita

1. Metti la copertina in `covers/<slug>.jpg` (quadrata, almeno 1200 px).
2. Aggiungi un blocco in `releases.json`:

```json
{
  "slug": "titolo-del-pezzo",
  "title": "TITOLO DEL PEZZO",
  "tagline": "una riga sotto la copertina",
  "date": "2026-12-01",
  "cover": "covers/titolo-del-pezzo.jpg",
  "links": {
    "spotify": "https://open.spotify.com/track/...",
    "applemusic": "https://music.apple.com/...",
    "youtube": "https://music.youtube.com/...",
    "more": "https://distrokid.com/hyperfollow/alexpalaz/...",
    "more_label": "YouTube · Amazon · Deezer · TIDAL"
  }
}
```

   Piattaforme riconosciute: `spotify`, `applemusic`, `youtube`, `amazon`, `deezer`, `tidal`, `soundcloud`, più `more` (link generico).

3. Genera e pubblica:

```sh
python3 tools/build.py
git add -A && git commit -m "Aggiunta <titolo>" && git push
```

La pagina sarà su `https://alexpalaz.github.io/music/<slug>/` dopo circa un minuto.

## Struttura

- `releases.json` — i dati: artista, pixel, elenco uscite. È l'unico file da toccare.
- `covers/` — copertine originali.
- `shared/style.css`, `shared/pixel.js` — stile e tracciamento comuni a tutte le pagine.
- `tools/release.html`, `tools/hub.html` — modelli; `tools/build.py` — generatore.
- `index.html`, `<slug>/` — output generato, non modificare a mano.

## Tracciare la provenienza dei click

Ogni pagina legge i parametri UTM dall'indirizzo e li allega agli eventi del Pixel Meta
(`ViewContent`, `Lead`, `Listen`) come `source`, `medium`, `campaign`, `ad`.
In Gestione eventi → evento → "Visualizza dettagli" si vedono i Lead divisi per sorgente.

Link da usare:

- Meta Ads (parametri URL dell'inserzione): `utm_source=meta&utm_medium=paid&utm_campaign=bombaka_test&utm_content={{ad.name}}`
- Bio Instagram: `https://alexpalaz.github.io/music/bombaka/?utm_source=instagram&utm_medium=bio`
- Bio TikTok: `https://alexpalaz.github.io/music/bombaka/?utm_source=tiktok&utm_medium=bio`
- Senza parametri → `source` vale `direct` (o `referral` se arriva da un altro sito).
