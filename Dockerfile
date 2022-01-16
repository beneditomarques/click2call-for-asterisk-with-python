FROM tiangolo/uvicorn-gunicorn:python3.6
COPY ./app /app
COPY init_api.sh /
RUN chmod +x /init_api.sh && pip install --no-cache-dir -r requirements.txt 
CMD ["/init_api.sh"]
