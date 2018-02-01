#!/usr/bin/env python
# coding:utf-8

from rediscluster import StrictRedisCluster
import sys

def redis_cluster():
    redis_nodes =  [{'host':'127.0.0.1','port':7001},
                    {'host':'127.0.0.1','port':7002},
                    {'host':'127.0.0.1','port':7003},
                    {'host':'127.0.0.1','port':7004},
                    {'host':'127.0.0.1','port':7005},
                    {'host':'127.0.0.1','port':7006}
                   ]
    try:
        redisconn = StrictRedisCluster(startup_nodes=redis_nodes)
    except Exception,e:
        print "Connect Error!"
        sys.exit(1)

    redisconn.set('name','admin')
    redisconn.set('age',18)
    print "name is: ", redisconn.get('name')
    print "age  is: ", redisconn.get('age')

redis_cluster()
