# Dixon Pool Service Preview

Static Website Rescue Stage 2 concept generated only from the verified Stage 1 record at `/home/chris/pitch-pipeline/01_scraped/dixon-pool-service.json` and its referenced assets.

## Build and verify

```bash
python3 build.py
python3 verify.py
```

Generated output is written to `public/`. Cloudflare Pages serves that directory directly. Web Analytics is configured at the Pages project level, so no analytics beacon is committed in source.

The campaign path is generated in `public/_redirects` as `/scan / 302`.
