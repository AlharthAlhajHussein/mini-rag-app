from fastapi import APIRouter, status, Request, HTTPException
from fastapi.responses import JSONResponse
from .schemes import PushRequest, SearchRequest
from models import ProjectModel, ChunkModel
from controllers import NLPCntroller
from models.enums.ResponseEnum import ResponseSignals
from views.nlp import NLPPushResponse, NLPInfoResponse, NLPSearchResponse, NLPAnswerResponse
from tqdm.auto import tqdm
import logging


logger = logging.getLogger('uvicorn.error')


nlp_router = APIRouter(
    prefix = '/api/v1/nlp',
    tags = ['nlp']
)

@nlp_router.post(
    "/index/push/{project_id}",
    response_model= NLPPushResponse,
    status_code= status.HTTP_200_OK,
    responses= {
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "ProjectNotFound": ResponseSignals.PROJECT_NOT_FOUND.value + f": {4}",
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "InsertIntoDBError": ResponseSignals.INSERT_INTO_DB_ERROR.value,
                    }
                }
            }
        }
    },
    summary="Index project chunks into vector database",
    description="This endpoint retrieves chunks of a project and indexes them into a vector database (embeddings). It supports batching to efficiently handle large datasets. The endpoint returns the total number of chunks successfully indexed. If the specified project does not exist, it returns a 404 error. If there is an issue during the indexing process, it returns a 500 error."
)
async def index_project(request: Request, project_id: int, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    chunk_model = ChunkModel(request.app.db_client)
    
    project = await project_model.get_project_or_create_one(project_id)
    if not project:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= ResponseSignals.PROJECT_NOT_FOUND.value + f": {project_id}"
        )
    
    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    
    # create collection if not exists
    collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
    
    _ = await nlp_controller.vector_db_client.create_collection(
        collection_name= collection_name,
        dimension=nlp_controller.embedding_client.embedding_size,
        do_reset=push_request.do_reset
    )
    
    # setup batching
    total_chunks_count = await chunk_model.get_total_chunks_count(project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Indexing chunks into vector db", position=0)
    
    while has_records:
        
        page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
            
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        is_inserted = await nlp_controller.index_into_vector_db(project, page_chunks)
        
        if not is_inserted:
            raise HTTPException(
                status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= ResponseSignals.INSERT_INTO_DB_ERROR.value
            )
        
        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)
        
    return NLPPushResponse(inserted_items_count=inserted_items_count)
    

@nlp_router.get(
    "/index/info/{project_id}",
    response_model= NLPInfoResponse,
    status_code= status.HTTP_200_OK,
    summary="Get vector database collection info for a project",
    description="This endpoint retrieves information about the vector database collection associated with a specific project. It returns details such as the number of indexed items, collection name, and other relevant metadata. If the specified project does not exist, it returns a 404 error."
)
async def get_project_index_info(request: Request, project_id: int):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    collection_info = await nlp_controller.get_collection_info(project)
    
    return NLPInfoResponse(collection_info=collection_info)
    
    
@nlp_router.post(
    "/index/search/{project_id}",
    response_model= NLPSearchResponse,
    status_code= status.HTTP_200_OK,
    responses= {
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "signal": ResponseSignals.VECTORDB_SEARCH_ERROR_OR_NOT_FOUND.value
                    }
                }
            }
        }
    },
    summary="Search in vector database collection for chunks relevant to a query",
    description= "This endpoint allows searching for relevant chunks in the vector database collection associated with a specific project based on a query text. It returns a list of relevant chunks along with their similarity scores. If there is an issue during the search process or if no relevant chunks are found, it returns a 500 error with an appropriate signal."
)
async def search_index(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    search_result = await nlp_controller.search_vector_db_collection(project, search_request.query_text, top_k=search_request.top_k)
    
    if not search_result:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= ResponseSignals.VECTORDB_SEARCH_ERROR_OR_NOT_FOUND.value
        )
    
    return NLPSearchResponse(results=search_result)
    
    
@nlp_router.post(
    "/index/answer/{project_id}",
    response_model= NLPAnswerResponse,
    status_code= status.HTTP_200_OK,
    responses= {
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "signal": ResponseSignals.RAG_ANSWER_ERROR.value
                    }
                }
            }
        }
    },
    summary="Generate answer for a query based on retrieved chunks from vector database collection",
    description= "This endpoint generates an answer for a given query based on the relevant chunks retrieved from the vector database collection associated with a specific project. It uses a retrieval-augmented generation (RAG) approach to provide a comprehensive answer. If there is an issue during the answer generation process, it returns a 500 error with an appropriate signal."
)
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest):
    
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser)
    
    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(project, search_request.query_text, top_k=search_request.top_k)

    if not answer:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= ResponseSignals.RAG_ANSWER_ERROR.value
        )
    
    return NLPAnswerResponse(answer=answer)


    


