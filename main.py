## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/TLTMI)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from transformers import pipeline

class Settings(BaseSettings):
    DEFAULT_SOURCE_LANG: str = "en"
    DEFAULT_TARGET_LANG: str = "ja"

settings = Settings()

class TranslationPipeline:
    def __init__(self, source_lang, target_lang):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.pipeline = None

    def load(self):
        self.pipeline = pipeline(
            "translation",
            model=f"Helsinki-NLP/opus-mt-{self.source_lang}-{self.target_lang}"
        )

    def translate(self, text):
        if not self.pipeline:
            self.load()
        
        translated = self.pipeline(text)
        return translated[0]['translation_text']

app = FastAPI()
pipelines = {}

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = settings.DEFAULT_SOURCE_LANG
    target_lang: str = settings.DEFAULT_TARGET_LANG

@app.post("/translate")
async def translate(request: TranslationRequest):
    pipeline_key = f"{request.source_lang}-{request.target_lang}"
    
    if pipeline_key not in pipelines:
        pipelines[pipeline_key] = TranslationPipeline(request.source_lang, request.target_lang)
    
    try:
        translation = pipelines[pipeline_key].translate(request.text)
        return {"translation": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)