# Copyright (c) 2023-2024 Westfall Inc.
#
# This file is part of Windstorm-Mage.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, and can be found in the file NOTICE inside this
# git repository.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

FROM python:3.11-slim

ENV WINDRUNNERHOST="http://windrunner-webhook.argo-events:12000/windrunner"
ENV WINDSTORMAPIHOST="http://windstorm-api-service.windstorm/"

WORKDIR /app

## Install python libraries
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install "psycopg[binary]"
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
COPY src src
CMD python src/main.py
