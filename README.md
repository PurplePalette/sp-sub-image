# sonolus-image-server
![Python Version](https://img.shields.io/badge/python-v3.8-blue)
![License](https://img.shields.io/badge/license-MIT-green)

image file trimming server for sonolus-fastapi
this server meant micro service to make preview jacket.


## Requirements

* Poetry(>=1.16)
* Python(>=3.8.x)
* Any S3 storage(Recommends [B2 Cloud Storage](https://www.backblaze.com/b2/cloud-storage.html) with [Cloudflare](https://cloudflare.com/))

## Development setup
```bash
git clone https://github.com/PurplePalette/sp-sub-image
cd sp-sub-image
cp .env_test .env
poetry install
docker-compose up -d
(stop sp-sub-image_main_1 container)
(Run venv)
python main.py
(or run pytest)
```

## Docs
- [API Spec / Stoplight](https://sonolus-core.stoplight.io/docs/sub-servers/YXBpOjUxODQ0MDcy-sonolus-image-server)
- [Detailed spec / Whimsical (TODO)](#)