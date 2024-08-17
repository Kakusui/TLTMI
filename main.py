## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/TLTMI)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in modules
import time
from typing import Optional
import asyncio

## third-party imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import pipeline
from transformers.pipelines import Pipeline
import uvicorn

class TranslationRequest(BaseModel):
    text:str
    source_lang:Optional[str] = None
    target_lang:Optional[str] = None
    model:Optional[str] = None
    keep_alive:Optional[int] = None

class PipelineCreateRequest(BaseModel):
    source_lang:Optional[str] = None
    target_lang:Optional[str] = None
    model:Optional[str] = None
    keep_alive:Optional[int] = None

class TranslationPipeline:
    def __init__(self, source_lang:Optional[str], target_lang:Optional[str], model:Optional[str] = None, keep_alive:Optional[int] = 300):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model = model
        self.pipeline:Optional[Pipeline] = None
        self.last_used:float = time.time()
        self.keep_alive = keep_alive if keep_alive else 300

    async def load(self):
        ## They can pass in a model otherwise language pair will be used
        if(not self.model):
            self.model = f"Helsinki-NLP/opus-mt-{self.source_lang}-{self.target_lang}"
        
        try:
            self.pipeline = await asyncio.to_thread(pipeline, "translation", model=self.model)
        except Exception as e:
            raise Exception(f"Failed to load pipeline: {str(e)}\nLikely the model {self.model} does not exist, check your language pairs or model name.")

    async def translate(self, text:str) -> str:
        """Translate text"""
        if(not self.pipeline):
            await self.load()

        assert self.pipeline is not None, "Pipeline is not loaded"
        
        translated = await asyncio.to_thread(self.pipeline, text)
        self.last_used = time.time()

        return translated[0]['translation_text'] # type: ignore

class PipelineManager:
    def __init__(self): 
        self.pipelines: dict[str, TranslationPipeline] = {}

    async def get_pipeline(self, key:str, source_lang:Optional[str], target_lang:Optional[str], model:Optional[str]) -> TranslationPipeline:
        """Get a pipeline, if it does not exist, create it"""

        pipeline, _ = await self.add_pipeline(key, source_lang, target_lang, model)

        pipeline.last_used = time.time()

        return pipeline
    
    async def add_pipeline(self, key:str, source_lang:Optional[str], target_lang:Optional[str], model:Optional[str], keep_alive:Optional[int] = 300) -> tuple[TranslationPipeline, bool]:
        """Add a new pipeline"""

        already_existed = False

        if(key not in self.pipelines):
            self.pipelines[key] = TranslationPipeline(source_lang, target_lang, model, keep_alive)

        else:
            already_existed = True

        try:

            ## perform a translation to check if the model exists
            translation = await self.pipelines[key].translate("...")

        except Exception as e:
            await self.remove_pipeline(key)
            raise Exception(f"Failed to load pipeline: {str(e)}\nLikely the model {model} does not exist, check your language pairs or model name.")

        return self.pipelines[key], already_existed

    async def remove_pipeline(self, key: str) -> bool:
        """Remove a pipeline"""

        existed = False

        if(key in self.pipelines):
            existed = True
            del self.pipelines[key]

        return existed

    async def cleanup_task(self):
        """Cleanup task to remove pipelines that have not been used for a certain amount of time"""
        while True:
            current_time = time.time()
            keys_to_remove = [key for key, pipeline in self.pipelines.items() 
                              if current_time - pipeline.last_used > pipeline.keep_alive]
            
            for key in keys_to_remove:
                await self.remove_pipeline(key)

            ## check every minute
            await asyncio.sleep(60)

app = FastAPI()
pipeline_manager = PipelineManager()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(pipeline_manager.cleanup_task())

@app.post("/tltmi/translate")
async def translate(request:TranslationRequest):
    """Translate text"""

    if(not request.source_lang or not request.target_lang):
        pipeline_key = request.model
    else:
        pipeline_key = f"{request.source_lang}-{request.target_lang}"

    assert pipeline_key is not None, HTTPException(status_code=400, detail="Either source_lang and target_lang or model must be provided")
    
    try:

        pipeline = await pipeline_manager.get_pipeline(pipeline_key, request.source_lang, request.target_lang, request.model)
        translation = await pipeline.translate(request.text)
        
        if(request.keep_alive):
            pipeline_manager.pipelines[pipeline_key].last_used = time.time()
        
        return JSONResponse(status_code=200, content={"translation": translation})
    
    except Exception as e:

        if("check your language pairs or model name" in str(e)):
            return JSONResponse(status_code=400, content={"error": str(e)})

        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tltmi/add_pipeline")
async def add_pipeline(request:PipelineCreateRequest):
    """Create a new translation pipeline"""
    
    if(not request.source_lang or not request.target_lang):
        pipeline_key = request.model
    
    else:
        pipeline_key = f"{request.source_lang}-{request.target_lang}"

    assert pipeline_key is not None, HTTPException(status_code=400, detail="Either source_lang and target_lang or model must be provided")

    try:
        _, already_exists = await pipeline_manager.add_pipeline(pipeline_key, request.source_lang, request.target_lang, request.model, request.keep_alive)
        
        if(already_exists):
            return JSONResponse(status_code=200, content={"message": f"Pipeline '{pipeline_key}' already exists."})
        
        else:
            return JSONResponse(status_code=201, content={"message": f"Pipeline '{pipeline_key}' created successfully."})

    except Exception as e:

        if("check your language pairs or model name" in str(e)):
            return JSONResponse(status_code=400, content={"error": str(e)})

        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tltmi/remove_pipeline/{pipeline_key}")
async def delete_pipeline(pipeline_key:str):
    """Remove a pipeline"""
    existed = await pipeline_manager.remove_pipeline(pipeline_key)

    if(existed):
        return JSONResponse(status_code=200, content={"message": f"Pipeline '{pipeline_key}' removed successfully."})
    
    else:
        return JSONResponse(status_code=404, content={"message": f"Pipeline '{pipeline_key}' does not exist."})
    
@app.delete("/tltmi/remove_all_pipelines")
async def delete_all_pipelines():
    """Remove all pipelines"""
    for key in pipeline_manager.pipelines.keys():
        await pipeline_manager.remove_pipeline(key)

    return JSONResponse(status_code=200, content={"message": "All pipelines removed successfully."})


@app.post("/tltmi/restart")
async def restart():
    """Restart the application, resetting all state"""
    global pipeline_manager

    await delete_all_pipelines()
    
    pipeline_manager = PipelineManager()
    
    asyncio.create_task(pipeline_manager.cleanup_task())
    
    return JSONResponse(status_code=200, content={"message": "Application restarted successfully."})

@app.get("/tltmi/list_pipelines")
async def list_pipelines():
    """List all active pipelines"""
    return JSONResponse(status_code=200, content={"pipelines": list(pipeline_manager.pipelines.keys())})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)