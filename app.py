import cv2
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
import base64
from io import BytesIO
#from typing_extensions import Annotated
#import argparse
#import os
import numpy as np
from datetime import datetime
import random
import warnings
import uvicorn
from fastapi import Depends, FastAPI
#from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mangum import Mangum
import boto3
#from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
import json
from PIL import Image


app = FastAPI()
handler = Mangum(app)


origins = [
    "http://localhost:5175",
      "ANY_OR_ALL_front_end_url"  # Update this to your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#api_key_1 = "a1b2c3d4e5"

warnings.filterwarnings("ignore")
def save_base64_to_s3(base64_data, bucket_name, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id="AKIASPWDOKNSB44BNA7P",
        aws_secret_access_key="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" # Add full S3 access to these keys
    )
    decoded_data = base64.b64decode(base64_data)

    try:
        s3.put_object(Body=decoded_data, Bucket=bucket_name, Key=file_name, ACL='public-read')
        
        
        object_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return object_url
    except Exception as e:
        return f'Error uploading to S3: {str(e)}'


def s3_uploader(base64_data):
    body = base64_data
    # Generate a random timestamp within a reasonable range
    random_timestamp = datetime.fromtimestamp(random.randint(0, 2**31-1))
    
    # Format the timestamp as a string
    formatted_timestamp = random_timestamp.strftime("%Y%m%d%H%M%S")
    
    # Generate a random number to add uniqueness
    random_number = random.randint(1000, 9999)
    bucket_name = "ai-processed-images"  # Replace with your specific S3 bucket name
    file_name = f"uploaded-image-{formatted_timestamp}-{random_number}.png"  # Replace with your desired file name

    object_url = save_base64_to_s3(body, bucket_name, file_name)
    return object_url

api_key_1 = "a1b2c3d4e5"

class ImageInput(BaseModel):
    image_base64: str

@app.post("/process_images")
async def process_images(image: ImageInput, key: str = Body(embed=True)):
    if key != api_key_1:
        raise HTTPException(status_code=401, detail="Invalid API key")
    try:


        img_path = BytesIO(base64.b64decode(image.image_base64))
        img = Image.open(img_path).convert("RGB")

        gray_img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        invert = cv2.bitwise_not(gray_img)
        blur = cv2.GaussianBlur(invert, (15, 15), 0)
        inverted_blur = cv2.bitwise_not(blur)
        sketch = cv2.divide(gray_img, inverted_blur, scale=256.0)
        processed_image_io = BytesIO()
        Image.fromarray(sketch).save(processed_image_io, format="PNG")
        processed_image_b64 = base64.b64encode(processed_image_io.getvalue())

        public_url = s3_uploader(processed_image_b64)

        return JSONResponse(content={"message": "Image processed successfully", "result_image": public_url})
    except Exception as e:
        return JSONResponse(content={"error": f"Error processing image: {str(e)}"}, status_code=500)
if __name__ == "__main__":
#   uvicorn.run(app)
   uvicorn.run(app, host="127.0.0.1", port=8080)