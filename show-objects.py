#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands


OBJECT_PATH = '.git/objects/'


class Base(object):
    """对象基类"""
    hash = None


class Blob(Base):
    """blob对象"""
    content = None

    @classmethod
    def load_from_cat_file(cls, hash, output):
        """从cat-file的输出加载"""
        object = cls()
        object.hash = hash
        object.content = output
        return object

    def __str__(self):
        return '<blob: %s>' % (self.content,)


class Tree(Base):
    """tree对象"""
    entries = []

    class Entry(object):
        """tree对象条目"""
        mode = None
        type = None
        hash = None
        fname = None

        def __str__(self):
            return self.fname

    @classmethod
    def load_from_cat_file(cls, hash, output):
        """从cat-file的输出加载"""
        object = Tree()
        for line in output.split('\n'):
            entry = Tree.Entry()
            entry.mode, entry.type, info = line.split(' ', 2)
            entry.hash, entry.fname = info.split('\t')
            object.entries.append(entry)
        return object


    def __str__(self):
        return '<tree: %s..>' % (str(self.entries[0]))


class Commit(Base):
    """commit对象"""
    tree = None
    parent = []
    author = None
    committer = None
    message = None

    @classmethod
    def load_from_cat_file(cls, hash, output):
        """从cat-file的输出加载"""
        object = cls()
        object.hash = hash
        info, object.message = output.split('\n\n')
        for line in info.split('\n'):
            key, val = line.split(' ', 1)
            if type(getattr(object, key)) is list:
                new_val = getattr(object, key) + [val]
            else:
                new_val = val
            setattr(object, key, new_val)
        return object

    def __str__(self):
        return '<commit: %s>' % (self.message,)


def get_object_by_hash(hash):
    """通过hash获取git对象"""
    type = commands.getoutput('git cat-file -t %s' % (hash,))
    output = commands.getoutput('git cat-file -p %s' % (hash,))
    cls = {'blob': Blob, 'tree': Tree, 'commit': Commit}[type]
    object = cls.load_from_cat_file(hash, output)

    return object


def get_objects():
    """获取git的所有对象
    返回对象组成的列表"""
    hashes = []

    prefixes = [i for i in os.listdir(OBJECT_PATH) if len(i) == 2]
    for prefix in prefixes:
        suffixes = os.listdir(os.path.join(OBJECT_PATH, prefix))
        hashes += [prefix + i for i in suffixes if len(i) == 38]

    objects = map(get_object_by_hash, hashes)

    return objects


def objects2dot(objects, dotfile):
    """将对象列表及关系转换为dot文件"""
    pass


def dot2png(dotfile, pngfile):
    """将dot文件转换为png文件"""
    pass


def main(dotfile, pngfile):
    """主函数"""
    objects = get_objects()
    objects2dot(objects, dotfile)
    dot2png(dotfile, pngfile)


if __name__ == '__main__':
    main('objects.dot', 'objects.png')
