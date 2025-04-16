FROM python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
COPY ./test_files /code/test_files
RUN fastapi run main.py --port 80 & sleep 4 ;python -m pytest
RUN rm database.db
RUN fastapi run main.py --port 80 & sleep 4 ; python populate.py
CMD ["fastapi", "run", "main.py", "--port", "8000"]
