#!/usr/bin/env python

from pprint import pprint  # noqa
from jinja2 import Template
import json
import sys


ACCUMULATABLE_CMDS = ['ENV', 'EXPOSE', 'ADD', 'COPY']
TAIL_CMDS = ['WORKDIR', 'CMD', 'EXPOSE']


def parse_dockerfile(path):
    parsed = []
    last_line_escaped = False
    last_command = ""
    last_args = []
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if last_line_escaped:
                parsed[-1]['args'] += "\n" + line
            else:
                splitted_line = line.replace('\t', ' ').split(' ')
                cmd = splitted_line[0]
                args = ' '.join(splitted_line[1:])
                if cmd in ACCUMULATABLE_CMDS:
                    last_args.append(args)
                    if cmd == last_command:
                        parsed[-1]['args'].append(args)
                    else:
                        parsed.append({
                            "cmd": cmd,
                            "args": last_args,
                        })
                        last_args = []
                    last_command = cmd
                else:
                    parsed.append({
                        "cmd": cmd,
                        "args": args,
                    })
                    last_command = ""
                    last_args = []
            if line.endswith('\\'):
                last_line_escaped = True
            else:
                last_line_escaped = False
    head = []
    tail = []
    for obj in parsed:
        if obj['cmd'] in TAIL_CMDS:
            tail.append(obj)
        else:
            head.append(obj)
    result = head + [{"cmd": "#", "args": '-------'}] + tail
    return result


TEMPLATES = {
    "FROM": "We gonna use `{args}` as a base.",

    "": "",

    "#nodoc": "",

    "#": "{args}",

    "RUN": """Execute:

```sh
{args}
```
""",

    "ADD": Template("""Copy from the repository dir:

```sh
{% for arg in args %}cp -r {{arg}}
{% endfor %}```
"""),

    "CMD": lambda args: type(args) in (list, dict) and Template("""To start the application execute:

```sh
{% for arg in args %}{{arg}} {% endfor %}
```
""").render(args=json.loads(args)) or Template("""To start the application execute:

```sh
{{args}}
```
""").render(args=args),

    "WORKDIR": "Working directory is: `{args}`",


    "ENV": Template("""Export environment variable{%if args|length > 1 %}s{%endif%}:

```sh
export {% for arg in args %}{{arg|replace(" ", "=")}}{%if not loop.last %} \\\n{%endif%}{% endfor %}
```
"""),

    "EXPOSE": Template("""Following port{%if args|length > 1 %}s{%endif%} will be used by the application:

```sh
{% for arg in args %}{{arg|replace(" ", "=")}}{%if not loop.last %}, {%endif%}{% endfor %}
```
"""),

}
TEMPLATES['COPY'] = TEMPLATES['ADD']


def render_dockerfile(parsed):
    rendered = ""
    for line in parsed:
        cmd = line['cmd']
        args = line['args']
        if cmd in TEMPLATES:
            template = TEMPLATES[cmd]
            if isinstance(template, Template):
                rendered += "\n\n" + TEMPLATES[cmd].render(args=args)
            elif isinstance(template, str):
                rendered += "\n\n" + TEMPLATES[cmd].format(args=args)
            elif hasattr(template, "__call__"):
                rendered += "\n\n" + TEMPLATES[cmd](args)

        else:
            rendered += "\n\n{cmd} {args}".format(cmd=cmd, args=args)

    return rendered


def main():
    if len(sys.argv) > 1:
        dockerfile_path = sys.argv[1]
    else:
        dockerfile_path = './Dockerfile'
    parsed = parse_dockerfile(dockerfile_path)
    rendered = render_dockerfile(parsed)
    print(rendered)


if __name__ == "__main__":
    main()
