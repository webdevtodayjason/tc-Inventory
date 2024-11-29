web: flask db stamp head || true && \
     flask db upgrade && \
     if [ ! -f .initialized ]; then \
       flask create-category && \
       flask create-cpus && \
       flask create-tags && \
       flask create-admin && \
       touch .initialized; \
     fi && \
     gunicorn --bind 0.0.0.0:8080 run:app 