# gitlab-runner-research

This script is a part of some research I did on abusing GitLab Runners. The full blog post and information is <a href="https://frichetten.com/blog/abusing-gitlab-runners/?pk_campaign=github">here</a>.

```
usage: hijack-runner.py [-h] [--target TARGET] [--register REGISTER] [--attack ATTACK] [--tag TAG]
                        [--clone]

Abuse GitLab Runners

optional arguments:
  -h, --help           show this help message and exit
  --target TARGET      The GitLab instance to target
  --register REGISTER  Register a token
  --attack ATTACK      Use Runner token to steal data
  --tag TAG            Taglist separated with commas
  --clone              Will clone the repo locally
```
