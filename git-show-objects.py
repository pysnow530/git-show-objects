#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import logging


OBJECT_PATH = '.git/objects/'


logging.basicConfig(
    filename='show-objects.log',
    fliemode='a+',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(message)s',
)


class Base(object):
    """对象基类"""
    hash = None


class Blob(Base):
    """blob对象"""
    content = None

    @classmethod
    def load_from_cat_file(cls, hash, output):
        """从cat-file的输出加载"""
        object_ = cls()
        object_.hash = hash
        object_.content = output
        return object_

    def __str__(self):
        if len(self.content) <= 6:
            return self.content
        else:
            return self.content[:3] + '...'


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
        object_ = Tree()
        object_.hash = hash
        for line in output.split('\n'):
            entry = Tree.Entry()
            entry.mode, entry.type, info = line.split(' ', 2)
            entry.hash, entry.fname = info.split('\t')
            object_.entries.append(entry)
        return object_


    def __str__(self):
        return '%d entries' % (len(self.entries),)


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
        object_ = cls()
        object_.hash = hash
        info, object_.message = output.split('\n\n')
        for line in info.split('\n'):
            key, val = line.split(' ', 1)
            if type(getattr(object_, key)) is list:
                new_val = getattr(object_, key) + [val]
            else:
                new_val = val
            setattr(object_, key, new_val)
        return object_

    def __str__(self):
        if len(self.message) <= 6:
            return self.message
        else:
            return self.message[:3] + '...'


def get_object_by_hash(hash):
    """通过hash获取git对象"""
    type = commands.getoutput('git cat-file -t %s' % (hash,))
    output = commands.getoutput('git cat-file -p %s' % (hash,))
    cls = {'blob': Blob, 'tree': Tree, 'commit': Commit}[type]
    object_ = cls.load_from_cat_file(hash, output)

    return object_


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
    dot = 'digraph {\n'
    for object_ in objects:
        if isinstance(object_, Blob):
            dot += '\thash_%s[shape=note, label="%s"];\n' % (object_.hash, str(object_))
        elif isinstance(object_, Tree):
            dot += '\thash_%s[shape=note, fontcolor="#2a77c0", label="%s"];\n' % (object_.hash, str(object_))
            for entry in object_.entries:
                dot += '\thash_%s -> hash_%s;\n' % (object_.hash, entry.hash)
        elif isinstance(object_, Commit):
            dot += '\thash_%s[shape=box, style=filled, fillcolor=orange, label="%s"];\n' % (object_.hash, str(object_))
            for parent_hash in object_.parent:
                dot += '\thash_%s -> hash_%s;\n' % (object_.hash, parent_hash)
            dot += '\thash_%s -> hash_%s;\n' % (object_.hash, object_.tree)
    dot += '}'

    open(dotfile, 'w+').write(dot)

    return dot


def dot2png(dotfile, pngfile):
    """将dot文件转换为png文件"""
    root, ext = os.path.splitext(dotfile)
    pngfile = root + '.png'
    output = commands.getoutput('dot -Tpng %s >%s' % (dotfile, pngfile))
    logging.debug(output)

    return pngfile


def main(dotfile, pngfile):
    """主函数"""
    objects = get_objects()
    objects2dot(objects, dotfile)
    dot2png(dotfile, pngfile)


if __name__ == '__main__':
    main('objects.dot', 'objects.png')
