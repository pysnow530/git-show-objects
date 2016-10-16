#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging
import commands


OBJECT_PATH = '.git/objects/'
EXPORT_PATH = '.git/obs/'


logging.basicConfig(
    filename='show-objects.log',
    fliemode='a+',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(message)s',
)


class Base(object):
    """对象基类"""
    hash = None

    @property
    def short_hash(self):
        """获取短hash"""
        return self.hash[:6]


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
            return '%s: %s' % (self.short_hash, self.content)
        else:
            return '%s: %s' % (self.short_hash, self.content[:3] + '...')


class Tree(Base):
    """tree对象"""
    entries = None

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
        object_.entries = []
        for line in output.split('\n'):
            entry = Tree.Entry()
            entry.mode, entry.type, info = line.split(' ', 2)
            entry.hash, entry.fname = info.split('\t')
            logging.debug('%s: add entry %s' % (object_.hash, entry.hash))
            object_.entries.append(entry)
        return object_


    def __str__(self):
        return '%s: %d entries' % (self.short_hash, len(self.entries),)


class Commit(Base):
    """commit对象"""
    tree = None
    parent = None
    author = None
    committer = None
    message = None

    @classmethod
    def load_from_cat_file(cls, hash, output):
        """从cat-file的输出加载"""
        object_ = cls()
        object_.hash = hash
        object_.parent = []
        object_.message = ''
        info, object_.message = output.split('\n\n')
        for line in info.split('\n'):
            key, val = line.split(' ', 1)
            if key == 'tree':
                object_.tree = val
            elif key == 'parent':
                object_.parent.append(val)
            elif key == 'author':
                object_.author = val
            elif key == 'committer':
                object_.cmmitter = val
            else:
                object_.message += val
        return object_

    def __str__(self):
        if len(self.message) <= 6:
            return '%s: %s' % (self.short_hash, self.message)
        else:
            return '%s: %s' % (self.short_hash, self.message[:3] + '...')


def init():
    """初始化工作：切换到工作目录，创建输出目录"""
    old_cwd = os.getcwd()
    while not os.path.isdir('.git'):
        os.chdir('..')

        new_cwd = os.getcwd()
        if old_cwd == new_cwd:
            raise Exception('Not a git repository (or any of the parent directories): .git')

        old_cwd = new_cwd

    if not os.path.isdir(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)


def get_object_by_hash(hash):
    """通过hash获取git对象"""
    type = commands.getoutput('git cat-file -t %s' % (hash,))
    cls = {'blob': Blob, 'tree': Tree, 'commit': Commit}[type]

    content = commands.getoutput('git cat-file -p %s' % (hash,))

    object_ = cls.load_from_cat_file(hash, content)

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
    cmd = 'dot -Tpng %s >%s' % (dotfile, pngfile)

    output = commands.getoutput(cmd)
    logging.debug('cmd: %s, output: %s' % (cmd, output))

    return pngfile


def main(dotfile, pngfile):
    """主函数"""
    objects = get_objects()
    objects2dot(objects, dotfile)
    dot2png(dotfile, pngfile)


if __name__ == '__main__':
    init()

    ts = time.time()
    dotfile = os.path.join(EXPORT_PATH, 'objects.dot')
    pngfile = os.path.join(EXPORT_PATH, 'objects_%d.png' % (ts,))
    main(dotfile, pngfile)
