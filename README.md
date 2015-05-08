# gitupcheck


#Usage

Append new item
```sh
python3.4 gitupcheck.py --path ../forked/foobar --remotepath https://github.com/saromanov/gitupcheck/ --store ../githublist
```

Append new item to redis
```sh
python3.4 gitupcheck.py --path ../forked/foobar --remotepath https://github.com/saromanov/gitupcheck/ --store @redis --addr localhost:6379
```

Getting changes

```sh
python3.4 gitupcheck.py --check ../githublist
```

Getting changes with redis

```sh
python3.4 gitupcheck.py --check @redis
```