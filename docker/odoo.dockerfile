FROM odoo:14
USER root
RUN apt-get update && apt-get install -y locales locales-all python3-dev build-essential libcurl4-openssl-dev libssl-dev
CMD "pip3 install -r /mnt/extra-addons/atenea/requirements.txt"