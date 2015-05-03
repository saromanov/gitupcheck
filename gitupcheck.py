from git import Repo,Git
import argparse
import logging
import os


#Usage without git module
#http://stackoverflow.com/questions/9774972/trying-to-execute-git-command-using-python-script

#python3.4 gitupcheck.py --check ../githublist
#python3.4 gitupcheck.py --path ../forked/celery --remotepath fun --store ../githublist

class GitUpCheck:
	def __init__(self, store=None):
		self.store = store

	def _getFromFile(self, path):
		''' Get infrormation about local and remote repos
		TODO. Append getting this info from redis
		'''
		f = open(path, 'r')
		for line in f.readlines():
			clearline = line.split('\n')[0].split(' ')
			remotepath = clearline[0]
			path = clearline[1]
			yield remotepath, path
		f.close()

	def _appendToFile(self, path, data):
		''' Write new item to store '''
		f = open(path, 'a')
		f.write('\n')
		f.write(data)
		f.close()

	def addItem(self, path, remotepath, store=None):
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
		check.execute(["git", "remote", "add", "upstream", remotepath])
		check.execute(["git", "fetch", "upstream"])
		self._appendToFile(store, remotepath+ ' ' + path)
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
		repos = self._getFromFile(self.store)
		for remotepath, path in repos: 
			print("Getting changes from {0} to {1}".format(remotepath, path))
			self._get_changes(path)


def main(results):
	path = results.path
	remotepath = results.remotepath
	checker = GitUpCheck()
	if path != None and remotepath != None and results.store != None:
		checker.addItem(path, remotepath, store=results.store)
	if results.check != None:
		checker.store = results.check
		checker.run()
	else:
		logging.error("Error in parsing arguments")

def parsing(parse):
	parse.add_argument("--path", help="Local path to repository")
	parse.add_argument("--remotepath", help="Remote path to repository")
	parse.add_argument("--store", help="Path to store with data")
	parse.add_argument("--check", help="Check current list. Argument path to list")
	main(parse.parse_args())

if __name__ == '__main__':
	parsing(argparse.ArgumentParser())