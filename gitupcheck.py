from git import Repo, Git
import argparse
import logging
import os

logging.basicConfig(
    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')


REDISNAME = '@redis'
DBNAME = 'gitupcheck'


class GitUpCheck:

    def __init__(self, store=None, addr='localhost:6379'):
        """ store - path to local file with format
        'remote path' 'local path'

            addr - address to remote store. Now supported is redis and in that case, addr can be 'localhost:6379'
        """
        self.store = store
        self.addr = addr

    def _getFromFile(self, path):
        ''' Get infrormation about local and remote repos
        '''
        f = open(path, 'r')
        for line in f.readlines():
            clearline = line.split('\n')[0].split(' ')
            remotepath = clearline[0]
            path = clearline[1]
            yield remotepath, path
            f.close()

    def _getData(self, store):
        """ Get data from local file or from remote store """
        if store == REDISNAME:
            checker = self._getFromRedis()
            result = list(
                map(lambda x: str(x).split(':'), self._getFromRedis()))
            return [(value[0][1:], value[1][:-1]) for value in result]
        return self._getFromFile(store)

    def _appendToFile(self, path, data):
        ''' Write new item to store '''
        log.info("Start read from file")
        f = open(path, 'a')
        f.write('\n')
        f.write(data)
        f.close()
        log.info("Complete read from file")

    def _prepareAddress(self):
        value = self.addr.split(':')
        host = value[0]
        port = value[1]
        return host, port

    def _appendToRedis(self, data):
        import redis
        host, port = self._prepareAddress()
        client = redis.Redis(host=host, port=port)
        client.lpush("gitupcheck", data)

    def _getFromRedis(self):
        import redis
        logging.info("Getting data from redis")
        host, port = self._prepareAddress()
        return redis.Redis(host=host, port=port).lrange('gitupcheck', 0, -1)

    def addItem(self, path, remotepath, store=None, addr=None):
        '''	Add and check new item
        store - path to file with information about local and remore repos
        path - local path to forked repository for example: ~/gitupcheck
        remotepath - path to remote repository for example: https://github.com/saromanov/gitupcheck
        '''
        if not os.path.exists(path):
            msg = "{0} not found".format(path)
            logging.debug(msg)
            raise Exception(msg)
        check = Git(path)
        print(check.execute(["git", "remote", "add", "upstream", remotepath]))
        check.execute(["git", "fetch", "upstream"])
        if store == '@redis':
            self.addr = addr
            self._appendToRedis(remotepath + ':' + path)
        else:
            self._appendToFile(store, remotepath + ' ' + path)
        print("Item was append: ")
        self._get_changes(path, gitclient=check)

    def _get_changes(self, path, gitclient=None):
        ''' Get and print changes from repository
        TODO. Remove Git client and get it with naive clear
        '''
        check = Git(path)
        if gitclient != None:
            check = gitclient
        print(check.execute(["git", "checkout", "master"]))
        print(check.execute(["git", "merge", "upstream/master"]), '\n')

    def run(self):
        ''' Start checking changes on repos
        '''
        repos = self._getData(self.store)
        logging.debug("Getting data from store: ")
        logging.debug(repos)
        for remotepath, path in repos:
            print("Getting changes from {0} to {1}".format(remotepath, path))
            self._get_changes(path)


def main(results):
    path = results.path
    remotepath = results.remotepath
    checker = GitUpCheck()
    if path != None and remotepath != None and results.store != None:
        checker.addItem(
            path, remotepath, store=results.store, addr=results.store)
    if results.check != None:
        checker.store = results.check
        if results.addr != None:
            checker.addr = results.addr
        checker.run()
    else:
        logging.error("Error in parsing arguments")


def parsing(parse):
    parse.add_argument("--path", help="Local path to repository")
    parse.add_argument("--remotepath", help="Remote path to repository")
    parse.add_argument("--store", help="Path to store with data")
    parse.add_argument(
        "--addr", help="Append address host:port to remote store")
    parse.add_argument(
        "--check", help="Check current list. Argument path to list")
    main(parse.parse_args())

if __name__ == '__main__':
    parsing(argparse.ArgumentParser())
