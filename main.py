from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory database for simplicity (use a real database in production)
users_db = []
posts_db = []


# Models
class User(BaseModel):
    username: str
    email: str
    password: str


class Post(BaseModel):
    title: str
    content: str
    author: str

# get all users
@app.get("/users")
def get_users():
    if not len(users_db) > 0:
        raise HTTPException(
            status_code=400, detail="No any users Registered")
    return users_db
    

# User Registration
@app.post("/auth/register", response_model=User)
async def register(user: User):
    # Check if the user already exists
    for existing_user in users_db:
        if existing_user["username"] == user.username or existing_user["email"] == user.email:
            raise HTTPException(
                status_code=400, detail="Username or email already exists")

    # Store the user in the database (for simplicity, we're using an in-memory list)
    users_db.append(user.dict())
    return user


# User Login (simulated for simplicity)
@app.post("/auth/login")
async def login(user: User):
    # Simulated login logic (you'd implement actual authentication here)
    for existing_user in users_db:
        if existing_user["username"] == user.username and existing_user["password"] == user.password:
            return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Login failed")


# Create a Post (authenticated endpoint)
@app.post("/posts", response_model=Post)
async def create_post(post: Post, user: User = Depends(login)):
    # Associate the post with the authenticated user
    post.author = user.username
    posts_db.append(post.dict())
    return post


# Update a specific post by its ID
@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, updated_post: Post, user: User = Depends(login)):
    # Check if the post with the given ID exists
    if post_id < 0 or post_id >= len(posts_db):
        raise HTTPException(status_code=404, detail="Post not found")

    existing_post = posts_db[post_id]

    # Check if the user is the author of the post (for authorization)
    if existing_post["author"] != user.username:
        raise HTTPException(
            status_code=403, detail="You are not the author of this post")

    # Update the post
    existing_post.update(updated_post.dict(exclude_unset=True))
    return existing_post


# Delete a specific post by its ID
@app.delete("/posts/{post_id}", response_model=Post)
async def delete_post(post_id: int, user: User = Depends(login)):
    # Check if the post with the given ID exists
    if post_id < 0 or post_id >= len(posts_db):
        raise HTTPException(status_code=404, detail="Post not found")

    existing_post = posts_db[post_id]

    # Check if the user is the author of the post (for authorization)
    if existing_post["author"] != user.username:
        raise HTTPException(
            status_code=403, detail="You are not the author of this post")

    # Delete the post
    deleted_post = posts_db.pop(post_id)
    return deleted_post


# Get All Posts
@app.get("/posts", response_model=List[Post])
async def get_posts():
    return posts_db


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
