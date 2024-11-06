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

# Windstorm-mage
## The purpose of this sensor is to take an input from each of the three
## winds (spear, sage, ripper) and determine which actions need to be run.
## For sage: Need to lookup all verifications with this input
## For ripper: Same
## For spear: Have to find the actions in the commit for this head.

from env import *

import time
start_time = time.time()

from datetime import datetime
from uuid import uuid4 as uuid_gen

import requests
import sqlalchemy as db
from sqlalchemy.orm import Session
from models import Thread_Executions

def connect():
    db_type = "postgresql"
    user = DBUSER
    passwd = DBPASS
    address = SQLHOST
    db_name = DBTABLE

    address = db_type+"://"+user+":"+passwd+"@"+address+"/"+db_name
    engine = db.create_engine(address)
    conn = engine.connect()

    return conn, engine

def spear(payload):
    if not 'ref' in payload:
        # This was blank, this is probably from a test build.
        return []

    print('Windspear -- finding all models on this branch: {}.'.format(payload['ref']))
    r = requests.get(
        WINDSTORMAPIHOST+"models/threads/branch_search/{}".format(
            payload['ref']
        )
    )
    try:
        if isinstance(r.json()["results"], dict):
            if "error" in r.json()["results"]:
                print('Error finding threads to execute, doing nothing.')
                return []
    except:
        print('Error finding threads to execute, doing nothing.')
        return []

    return r.json()["results"], False

def sage(payload):
    print('Windsage -- finding all models matching: {}.'.format(payload['artifact_id']))
    r = requests.get(
        WINDSTORMAPIHOST+"models/threads/artifact_search/{}".format(
            payload['artifact_id']
        )
    )
    try:
        if isinstance(r.json()["results"], dict):
            if "error" in r.json()["results"]:
                print('Error finding threads to execute, doing nothing.')
                return []
    except:
        print('Error finding threads to execute, doing nothing.')
        return []

    return r.json()["results"], True

def ripper(payload):
    print('Windripper -- finding all models matching: {}.'.format(payload['container_id']))
    r = requests.get(
        WINDSTORMAPIHOST+"models/threads/container_search/{}".format(
            payload['container_id']
        )
    )
    try:
        if isinstance(r.json()["results"], dict):
            if "error" in r.json()["results"]:
                print('Error finding threads to execute, doing nothing.')
                return []
    except:
        print('Error finding threads to execute, doing nothing.')
        return []

    return r.json()["results"], True

def post_threads(source, threads, force):
    ''' Take each action and post to start workflows.

    threads: list of dictionaries
        dict:
            'id': id of an action/workflow
            'dependency': id of an action this action depends on output from
    '''
    if len(threads) == 0:
        print('--No threads to generate.')
        return

    for action in threads:
        if action['dependency'] is None or force:
            # If coming from windripper or windsage, run this dependent task anyway
            print('--Starting thread: {}'.format(action['id']))
            # Get the thread data

            c, engine = connect()
            dtn = datetime.now()
            with Session(engine) as session:
                te = Thread_Executions(
                    name = str(uuid_gen()),
                    action_id = action["id"],
                    model_commit_id = action["model_commit_id"],
                    container_commit_id = action["container_commit_id"],
                    artifact_commit_id = action["artifact_commit_id"],
                    source = source,
                    state = 'windstorm',
                    date_created = dtn,
                    date_updated = dtn,
                )
                session.add(te)
                session.commit()
                session.refresh(te)

            c.close()
            engine.dispose()

            r = requests.get(
                WINDSTORMAPIHOST+"models/threads/thread/{}?validate=true".format(
                    action['id']
                )
            )
            if isinstance(r.json()["results"], dict):
                if "error" in r.json()["results"]:
                    # Skip this one
                    print('Error found: {}'.format(r.json()["results"]["error"]))
                    continue

            # Post it to windrunner
            try:
                requests.post(WINDRUNNERHOST, json = {
                    'action': r.json()["results"][0],
                    'thread_execution': te.id,
                    'prev_thread_name': None})
            except:
                print('Could not reach next endpoint but sensor executed correctly.')
        else:
            print('Found dependent action, skipping. This will be run from thread {}.'.format(action['dependency']))

    return

def main(source="spear", payload={}):
    print('Processing webhook')
    if source == "spear":
        threads, force = spear(payload)
    elif source == "sage":
        threads, force = sage(payload)
    elif source == "ripper":
        threads, force = ripper(payload)

    print('Sending threads')
    post_threads(source, threads, force)

    return

if __name__ == '__main__':
    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
