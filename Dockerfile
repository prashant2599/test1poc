FROM public.ecr.aws/lambda/python:3.9.2023.06.27.12-x86_64

RUN yum install -y git

COPY app.py .

CMD ["app.lambda_handler"]