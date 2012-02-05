#!/usr/bin/env python

import os
import random
import subprocess
import tempfile

_NUM_COMMITS = 4000000
_NUM_FILES = 1300000

_GIT = '~/repos/git/git'

class File(object):
  def __init__(self):
    with open('nouns.txt') as fh:
      self.nouns = [line.strip() for line in fh.readlines()]

  def create(self, name):
    with open(name, 'w') as fh:
      for i in range(10):
        to_write = ''
        for j in range(random.randrange(5, 21)):
          k = random.randrange(0, len(self.nouns))
          to_write += self.nouns[k]
          to_write += ' '
        to_write += '\n'
        fh.write(to_write)

  def modify(self, name):
    lines = list()
    with open(name, 'r') as fh:
      lines = fh.readlines()

    first_line_to_modify, second_line_to_modify =\
        sorted(random.sample(range(len(lines)), 2))
    
    first_line = self._modify_line(first_line_to_modify, lines)
    second_line = self._modify_line(second_line_to_modify, lines)

    with open(name, 'w') as fh:
      for i in range(len(lines)):
        if i == first_line_to_modify:
          fh.write(first_line)
        elif i == second_line_to_modify:
          fh.write(second_line)
        else:
          fh.write(lines[i])

  def _modify_line(self, line_index, lines):
    line = lines[line_index]
    seek_point = random.randrange(len(line))
    to_write = line[:seek_point]
    for j in range(random.randrange(5, 21)):
      k = random.randrange(0, len(self.nouns))
      to_write += self.nouns[k]
      to_write += ' '
    to_write += line[seek_point:]
    return to_write

def random_file(directory):
  try:
    files = [os.path.join(path, filename)
             for path, dirs, files in os.walk(directory)
             for filename in files
             if '.git' not in path]

    return random.choice(files)
  except IndexError:
    return None

subprocess.Popen('rm -rf /tmp/test', shell=True).wait()
subprocess.Popen('mkdir /tmp/test', shell=True).wait()
fm = File()
os.chdir('/tmp/test')
subprocess.Popen('git init', shell=True).wait()
# Until we have 4 million commits.
for commit in range(_NUM_COMMITS):
  # Queue tasks to do.
  tasks = list()

  # Tasks modify 2-5 files, create a file occasionally.
  for i in range(random.randrange(2, 6)):
    r_file = random_file('/tmp/test')
    if not r_file or random.randrange(0, 10) <= 2:
      temp = tempfile.NamedTemporaryFile(dir='/tmp/test/', delete=False)
      tasks.append(('CREATED', temp.name))
    else:
      tasks.append(('MODIFY', r_file))

  # Execute tasks
  for task in tasks:
    if 'CREATED' == task[0]:
      # write lines into the file
      fm.create(task[1])
      subprocess.Popen('git add *', shell=True).wait()
    elif 'MODIFY' == task[0]:
      # Modify means change exist lines and add a few lines at the end filled with
      # dictionary words.
      fm.modify(task[1])

  subprocess.Popen('git commit -am \'Commit number %d.\'' % commit, shell=True).wait()

# Commit.
