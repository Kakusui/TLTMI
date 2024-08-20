# TLTMI (That Local Translation Model Interface)

## Last version: 0.0.1

## A work in progress 

TLTMI is an open-source project aimed at providing an easy-to-deploy, locally-run translation service that can be accessed via a simple url fetch. It combines the power of state-of-the-art machine translation models with the convenience of containerized deployment.

Currently TLTMI is focusing on using the Helsinki-NLP/Opus-MT models for translation. These are efficient, memory-light models that can be easily loaded into memory for quick translation.

They are sufficient for most translation tasks, but TLTMI is aiming to be an option for local translation when cost is a concern and proprietary, api-based translation services are not an option.

### *Planned* Features

- Dockerized translation service for easy deployment
- Support for multiple language pairs
- FastAPI-based REST API for translation requests
- Local processing for enhanced privacy and offline capability
- Easy Model handling (discard, get, create, etc)

### Getting Started

#### Prerequisites

- Docker

#### Pulling the Docker Image

Pull the Docker image from Docker Hub

[Link](https://hub.docker.com/repository/docker/bikatr7/tltmi-core/general)


``` bash
docker pull bikatr7/tltmi-core:v0.0.1
```
or

```bash
docker pull bikatr7/tltmi-core:latest
```

then run with

```bash
docker run bikatr7/tltmi-core:v0.0.1
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

**ALL** endpoints are currently under `/tltmi`

### Some notes

* Model and pipeline are interchangeable in this context
* Models are created on demand if one does not exist already
* Models are stored in memory and are not saved to disk
* Models created by a `model` parameter are separate from those created by `source_lang` and `target_lang` parameters (Meaning if you create the exact same model with `model` and `source_lang` and `target_lang` they will be separate models)

### Translating Text

Pretty self-explanatory, just send a POST request to the `/tltmi/translate` endpoint with a similar looking json payload as below:

```bash
curl -X POST "http://localhost:8000/tltmi/translate" -H "Content-Type: application/json" -d '{"text": "I am really tired today.", "source_lang": "en", "target_lang": "jap"}'
```

Note that language codes *currently* are based on the Helsinki-NLP/Opus-MT models which are inconsistent. TLTMI will try to load whatever you give it and will warn you if it's invalid.

There are thousands of pairs, it is not feasible for TLTMI to keep track of valid ones. This is up to you.

### Pipeline management

`/tltmi/add_pipeline` expects source_lang and target lang OR model, also an optional keep_alive parameter

`tltmi/remove_pipeline/{pipeline_key}` expects a key, removes the existing model.

`/tltmi/remove_all_pipelines` removes all pipelines
 
`/tltmi/list_pipelines` Returns all pipelines

### Admin

`/tltmi/restart` If for some reason you break something but don't want to kill the server, call this.

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
- Helsinki-NLP/Opus-MT for their amazing work on the models used in this project.