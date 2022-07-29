from fastapi import FastAPI, HTTPException
from mongita import MongitaClientDisk
from pydantic import BaseModel

class Shape(BaseModel):
    name: str
    no_of_sides: int
    id: int

app = FastAPI()

client = MongitaClientDisk()
db = client.db   
shapes = db.shapes 

#delete database with rm -Rf ~/.mongita


@app.get("/") #get decorator maps function to an endpoint
async def root(): #fastapi supports async, needs Asynce Server Gateway Interface, uvicorn can do this
# Flask implements Web Server Gateway Interface
    return {"message": "Hello world"}
    # FastAPI will translate this dictionary into a JSON for you:
    # '{"message": "Hello world"}'
    # and return it in a http response with appropriate http status code
    # Response 200 OK '{"message": "Hello world"}'

@app.get("/shapes")
async def get_shapes():
    existing_shapes = shapes.find({})
    return [
            {
                key: shape[key] for key in shape if key != "_id"
            }
        for shape in existing_shapes
    ]

# FAST API makes extensive use of pydantic and type hints
# path parameters -> variable paths
# all path parameters without type hints are assumed to be strings
@app.get("/shapes/{shape_id}")
async def get_shapes_by_id(shape_id: int):
    if shapes.count_documents(
        {
            "id": shape_id
        }
    ) > 0:
        shape = shapes.find_one(
            {
                "id": shape_id
            }
        )
        return {
            key:shape[key] for key in shape if key != "_id"
        }
    raise HTTPException(
        status_code=404,
         detail=f"No shape with id {shape_id} found"
    )

@app.post("/shapes")
async def post_shape(shape: Shape):
    shapes.insert_one(shape.dict())
    return shape # return newly inserted item in body (convention)

@app.put("/shapes/{shape_id}")
async def update_shape(shape_id: int, shape: Shape):
    if shapes.count_documents({"id": shape_id}) > 0:
        shapes.replace_one(
            {
                "id": shape_id
            }, 
            shape.dict()
        )
        return shape # return newly inserted item in body (convention)
    raise HTTPException(
        status_code=404,
        detail=f"No shape with id {shape_id} found"
    )

@app.put("/shapes/upsert/{shape_id}")
async def update_shape(shape_id: int, shape: Shape):
    shapes.replace_one(
        {
            "id": shape_id
        }, 
        shape.dict(), 
        upsert=True
    )
    return shape # return newly inserted item in body (convention)

@app.delete("/shapes/{shape_id}")
async def delete_shape(shape_id: int):
    delete_result = shapes.delete_one({"id": shape_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No shape with {shape_id} exists"
        )
    return {
        "OK": True
    }