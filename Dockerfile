FROM jupyter/scipy-notebook:python-3.10.8 as base

RUN pip install nb_black
RUN pip install shapely

FROM base as debug
RUN pip install debugpy

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:8889", "--wait-for-client", "main.py"]

FROM base as prod

CMD ["jupyter", "lab", "--ip", "0.0.0.0"]
