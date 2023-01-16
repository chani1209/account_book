FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install sqlalchemy
RUN pip install "python-jose[cryptography]"
RUN pip install "passlib[bcrypt]"

ENTRYPOINT ["uvicorn", "main:app","--reload", "--reload-dir", "/code", "--host", "0.0.0.0", "--port"]
