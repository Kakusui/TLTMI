## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/TLTMI)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from transformers import pipeline
from transformers.pipelines import Pipeline

import uvicorn



class TranslationRequest(BaseModel):
    text:str
    source_lang:str | None = None
    target_lang:str | None = None
    model:str | None = None


class TranslationPipeline:
    source_lang:str | None
    target_lang:str | None
    pipeline:Pipeline | None
    model:str | None

    def __init__(self, source_lang:str | None, target_lang:str | None, model:str | None = None):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model = model
        self.pipeline = None

        if(not self.source_lang or not self.target_lang):
            if(not self.model):
                raise Exception("Either source_lang and target_lang or model must be provided")
        

    def load(self):

        ## They can pass in a model otherwise language pair will be used
        if(not self.model):
            self.model = f"Helsinki-NLP/opus-mt-{self.source_lang}-{self.target_lang}"

        try:

            self.pipeline = pipeline(
                "translation",
                model=self.model
            )

        except Exception as e:
            raise Exception(f"Failed to load pipeline: {str(e)}\nLikely the model {self.model} does not exist, check your language pairs or model name")

    def translate(self, text:str) -> str:
        if(not self.pipeline):
            self.load()

        assert self.pipeline is not None, "Pipeline is not loaded"
        
        translated = self.pipeline(text)
        return translated[0]['translation_text'] # type: ignore (not dealing with this lmfao)

app = FastAPI()
pipelines:dict[str, TranslationPipeline] = {}

@app.post("/tltmi/translate")
async def translate(request:TranslationRequest):

    if(not request.source_lang or not request.target_lang):
        pipeline_key = request.model

    else:
        pipeline_key = f"{request.source_lang}-{request.target_lang}"

    assert pipeline_key is not None, "Pipeline key is None"
    
    if(pipeline_key not in pipelines):
        pipelines[pipeline_key] = TranslationPipeline(request.source_lang, request.target_lang, request.model)
    
    try:
        translation = pipelines[pipeline_key].translate(request.text)
        return {"translation": translation}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if(__name__ == "__main__"):
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)