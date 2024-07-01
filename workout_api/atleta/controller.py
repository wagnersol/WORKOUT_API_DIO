import datetime 
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdade
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/',
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency,
    atleta_in:AtletaIn = Body(...)
):
  
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome
    atleta_cpf = atleta_in.cpf

    categoria = (await db_session.execute( 
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()

    if not categoria:
          raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail=f'A categoria {categoria_nome}não foi encontrada.'
        )
    
    centro_treinamento = (await db_session.execute( 
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()

    if not centro_treinamento:
          raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail=f'O centro de treinamento {centro_treinamento_nome}não foi encontrado.'
        )
    
    atleta = (await db_session.execute( 
        select(AtletaModel).filter_by(cpf=atleta_cpf))
    ).scalars().first()

    if atleta:
          raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um atleta cadastrado com o cpf:{atleta_cpf}.'
        )

     
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
    
        db_session.add( atleta_model)
        await db_session.commit()
    except Exception:    
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco.'
        )
    return  atleta_out

@router.get(
    '/',
    summary='Consultar todas os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[ AtletaOut],
)
async def query(
    db_session: DatabaseDependency) -> list[ AtletaOut]:
    atletas:list[ AtletaOut] = (await db_session.execute( select(AtletaModel))).scalars().all()
    
    return [AtletaOut.model_validate(atleta) for atleta in atletas]


@router.get(
    '/{id}',
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta:AtletaOut = (
        await db_session.execute( select(AtletaModel).filter_by(id=id))
    ).scalars().first()
    
    if not  atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encomtrado no id: {id}'
        )

    return  atleta

@router.patch(
    '/{id}',
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdade = Body(...)) -> AtletaOut:
    atleta:AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()
    
    if not  atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encomtrad no id: {id}'
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, Value in atleta_update.items():
        setattr(atleta, key, Value)
    await db_session.commit()
    await db_session.refresh(atleta)

    return  atleta

@router.delete(
    '/{id}',
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT,
    
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta:AtletaOut = (
        await db_session.execute( select(AtletaModel).filter_by(id=id))
    ).scalars().first()
    
    if not  atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encomtrado no id: {id}'
        )

    await db_session.delete(atleta)
    await db_session.commit()
   

@router.get(
    '/{nome}',
    summary='Consulta um Atleta pelo Nome',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(nome: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta:AtletaOut = (
        await db_session.execute( select(AtletaModel).filter_by(nome=nome))
    ).scalars().first()
    
    if not  atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encomtrado pelo nome: {nome}'
        )

    return  atleta

@router.get(
    '/{cpf}',
    summary='Consulta um Atleta pelo CPF',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(cpf: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta:AtletaOut = (
        await db_session.execute( select(AtletaModel).filter_by(cpf=cpf))
    ).scalars().first()
    
    if not  atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encomtrado pelo CPF: {cpf}'
        )

    return  atleta
