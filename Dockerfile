FROM python:3.9.10
WORKDIR /Webpage_UHealth
COPY app.py helper.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "./app.py"]

