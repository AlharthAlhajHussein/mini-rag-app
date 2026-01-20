from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from .schemes import PushRequest, SearchRequest
from models import ProjectModel, ChunkModel
from controllers import NLPCntroller
from models.enums.ResponseEnum import ResponseSignals
import logging


logger = logging.getLogger('uvicorn.error')


nlp_router = APIRouter(
    prefix = '/api/v1/nlp',
    tags = ['api_v1','nlp']
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    
    chunk_model = ChunkModel(request.app.database)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content = {"signal": ResponseSignals.PROJECT_NOT_FOUND.value} 
        )
    
    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    
    while has_records:
        
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
            
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_into_vector_db(project, page_chunks, chunks_ids=chunks_ids, do_reset=push_request.do_reset)
        
        if not is_inserted:
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content = {"signal": ResponseSignals.INSERT_INTO_DB_ERROR.value} 
            )

        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content= {
            "signal": ResponseSignals.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted items count": inserted_items_count
        }
    )
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    collection_info = nlp_controller.get_collection_info(project)
    
    return JSONResponse(
        content= {
            "signal": ResponseSignals.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection info": collection_info
        }
    )
    
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    search_result = nlp_controller.search_vector_db_collection(project, search_request.query_text, top_k=search_request.top_k)
    
    if not search_result:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content = {"signal": ResponseSignals.VECTORDB_SEARCH_ERROR_OR_NOT_FOUND.value} 
        )
    
    return JSONResponse(
        content= {
            "signal": ResponseSignals.VECTORDB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in search_result]
        }
    )
    
    
@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):
    
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser)
    
    answer, full_prompt, chat_hisroty = nlp_controller.answer_rag_question(project, search_request.query_text, top_k=search_request.top_k)

    if not answer:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content = {"signal": ResponseSignals.RAG_ANSWER_ERROR.value} 
        )
    
    return JSONResponse(
        content= {
            "signal": ResponseSignals.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_hisroty
        }
    )


    


