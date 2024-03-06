FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Adjusted the path to copy the 'src' directory

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

COPY ./* ./AB101/

COPY __init__.py .

CMD [ "app.handler" ]
