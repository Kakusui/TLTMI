# TLTMI (That Local Translation Model Interface)

## A work in progress 

TLTMI is an open-source project aimed at providing an easy-to-deploy, locally-run translation service that can be accessed via a simple url fetch. It combines the power of state-of-the-art machine translation models with the convenience of containerized deployment.

A proper readme will come later, but for now you can deal with my sarcasm as it's 4am and I'm tired.

### *Planned* Features

- Dockerized translation service for easy deployment
- Support for multiple translation models (Going to stick with Helsinki-NLP/Opus-MT for now)
- FastAPI-based REST API for translation requests
- Local processing for enhanced privacy and offline capability
- Easy Model handling (discard, get, load, timed discard, etc)
- More once my brain works

### Getting Started

#### Some notes

Memory hungry, be careful which switching language pairs right now (this is just a proof of concept so there's no performance optimization yet).

Every language pair switch loads another model into memory, so if you're running this on a machine with limited memory, be careful or bad things will happen (probably).

I'll fix this in the future, but for now, it's a proof of concept.

#### Prerequisites

- Docker
- A lack of sanity
- Time
- A decent amount of memory (6gb or so, currently just uses whatever memory is available. One model or so is roughly 2gb of memory)

#### Production Setup (If you're insane to do this right now)

Pull the Docker image from Docker Hub:

``` bash
docker pull bikatr7/tltmi-core:latest
```
or

```bash
docker pull bikatr7/tltmi-core:latest
```

then run with

```bash
docker run bikatr7/tltmi-core:v0.0.1-alpha
```

or

```bash
docker run bikatr7/tltmi-core:latest
```
  
#### Local Setup

Clone the repository:
   ```bash
   git clone https://github.com/kakusui/tltmi.git
   cd tltmi
   ```

##### Docker Method

1. Build the Docker image:
   ```bash
   docker build -t tltmi-core .
   ```

3. Run the container:
   ```bash
   docker run -d -p 8000:8000 tltmi-core
   ```

##### Local Method (Development)

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   python main.py
   ```

### Usage

Pretty self-explanatory, just send a POST request to the `/translate` endpoint with a similar looking json payload as below:

```bash
curl -X POST "http://localhost:8000/translate" -H "Content-Type: application/json" -d '{"text": "I really fucking hate Japanese!", "source_lang": "en", "target_lang": "jap"}'
```

Note that language codes *currently* are based on the Helsinki-NLP/Opus-MT models which are inconsistent at best.

japanese for instance should either be ja or jp right? No Jap for some reason. Have fun, I know I did

Anyways TLTMI does not do any checking of these and if you're using this at 0.0.1 alpha you have my condolences

### Contributing

This project is going to be slowly _but_ surely worked on over time. If you'd like to be involved feel free to contact me at [kadenbilyeu@proton.me](mailto:kadenbilyeu@proton.me).

### License

As Kakusui is an avid supporter of open-source software, this project is licensed under one of the strongest copyleft licenses available, the GNU Affero General Public License (AGPLv3).

You can find the full text of the license in the [LICENSE](License.md) file.

The AGPLv3 is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project, as well as any software that interacts with users over a network, must also be distributed under the same AGPLv3 license. This license grants you the freedom to use, modify, and distribute the software.

Please note that this information is a brief summary of the AGPLv3. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.

### Acknowledgments

- This project uses models from the Hugging Face Transformers library.
- Special thanks to the open-source community for their invaluable contributions to the field of machine translation.