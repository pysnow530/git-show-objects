# git-show-objects readme

> Git-show-objects is a extend git command, it aims to visualize git objects and it's relationship.

> Decompress gc pack is not supported yet.

## dependencies

* ImageMagic: translate dot file to png file
* open: mac command, for view png file

## features

* [x] draw objects
* [x] draw objects relationship
* [x] export png and view
* [x] draw index and relationship with objects
* [x] draw branch and relationship with objects

## snapshot

![objects.png](snapshot/objects.png)

## install

1. clone the repo

        git clone git@github.com:pysnow530/git-show-objects.git

2. add repo to path

        # add repo path to PATH environment
        echo 'export $PATH=REPO_PATH:$PATH' >>~/.profile

        # or link REPO_PATH/git-show-objects to bin
        ln -s REPO_PATH/git-show-objects /usr/local/bin/

3. use it

        cd some_repo
        git show-objects
