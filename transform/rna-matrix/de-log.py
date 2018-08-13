#!/usr/bin/env python3


import sys
import json


if __name__ == "__main__":
    with open(sys.argv[1]) as handle:
        with open(sys.argv[2], "w") as out:
            for line in handle:
                data = json.loads(line)
                n = {}
                for k, v in data['data']['values'].items():
                    if v == 0:
                        n[k] = 0
                    else:
                        n[k] = pow(v, 2) - 1.0
                data['data']['values'] = n
                out.write(json.dumps(data) + "\n")
