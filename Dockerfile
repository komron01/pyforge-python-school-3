FROM continuumio/miniconda3

# creating folder
WORKDIR /app

COPY requirements.txt .

RUN pip install  -r requirements.txt

# installing rdkit
RUN conda install -c conda-forge rdkit

# src -> to container 
COPY src /app/src

# openning ports
EXPOSE 8000

# running via uvicorn the app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
