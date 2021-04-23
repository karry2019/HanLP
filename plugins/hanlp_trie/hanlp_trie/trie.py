# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2020-01-04 23:46
from typing import Dict, Any, List, Tuple, Sequence, Union, Iterable, Optional


# 节点（Node）三要素：对应边（key）、自己的子节点（字典：_children）、是否代表一个词（用value标识，暂时让value=None，表示不代表一个词）
class Node(object):
    def __init__(self, value=None) -> None:
        """A node in a trie tree.

        Args:
            value: The value associated with this node.
        """
        self._children = {}  # 词典结构：字典键:边所对应的单字（字符）；字典值：子节点对象（Node实例）#节点所持有的数据（用于标识是否是终结点 / 是否代表一个词）
        self._value = value

    # 需要添加的字典点所属的边值（char）如果在当前节点中存在，就考虑复写；如果不存在，就根据char和value的值往当前节点的子节点字典中添加一个新的子节点
    # 添加子节点需要一个字符一个字符的添加
    def _add_child(self, char, value, overwrite=False):
        """
        Args:
            char: 需要添加的子节点的边对应的字符，即字典self._children中的键
            value: 用于标识添加的子节点是否是一个词的终点，None表示非；即字典self._children中的值（Node对象）所包含的_value值
        """
        child = self._children.get(char)
        if child is None:
            child = Node(value)
            self._children[char] = child
        elif overwrite:
            child._value = value
        return child

    # 确定有限状态自动机：key-需要查询的字符串（词）；返回结果如果为None，则说明为查询到对应的节点（不是词），否则反之
    def transit(self, key):
        """Transit the state of a Deterministic Finite Automata (DFA) with key.
            用于状态转移之前，在当前节点的子节点字典中寻找key（单子或词）是否存在

        Args:
            key: A sequence of criterion (tokens or characters) used to transit to a new state.

        Returns:
            A new state if the transition succeeded, otherwise ``None``.

        """
        state = self
        for char in key:
            state = state._children.get(char)
            if state is None:
                break
        return state

    def _walk(self, prefix: str, ordered=False):
        for char, child in sorted(self._children.items()) if ordered else self._children.items():
            prefix_new = prefix + char
            if child._value:
                yield prefix_new, child._value
            yield from child._walk(prefix_new)


class Trie(Node):
    def __init__(self, tokens: Optional[Union[Dict[str, Any], Iterable[str]]] = None) -> None:
        """A referential implementation of the trie (:cite:`10.1145/1457838.1457895`) structure. It stores a dict by
        assigning each key/value pair a :class:`~hanlp_trie.trie.Node` in a trie tree. It provides get/set/del/items
        methods just like a :class:`dict` does. Additionally, it also provides longest-prefix-matching and keywords
        lookup against a piece of text, which are very helpful in rule-based Natural Language Processing.

        Args:
            tokens: A set of keys or a dict mapping.
        """
        super().__init__()
        self._size = 0
        if tokens:
            if isinstance(tokens, dict):
                for k, v in tokens.items():
                    self[k] = v
            else:
                for k in tokens:
                    self[k] = True  # True会复制到终点子节点上

    # 这里的key代表的是需要查的词（一到多个字符不等）
    def __contains__(self, key):
        return self[key] is not None

    # 获取经过状态转移之后的节点所对应的value值，如果为None，则说明查询的词不存在（因为我们约定，None表示查询的词不存在）
    def __getitem__(self, key):
        state = self.transit(key)
        if state is None:
            return None
        return state._value

    # key-需要添加的字符串（词），value-对应的节点上的值，约定None代表该节点不是一个词的终点
    def __setitem__(self, key, value):
        state = self
        for i, char in enumerate(key):
            if i < len(key) - 1:
                state = state._add_child(char, None, False)  # 路径子节点
            else:
                state = state._add_child(char, value, True)  # 终点子节点
        self._size += 1  # 字典树词数量累加

    # 并不是真正的删除操作，属于逻辑删除范畴，删除一个词，说白了就是把终节点上的value值置空，让_value=None
    def __delitem__(self, key):
        state = self.transit(key)
        if state is not None:
            state._value = None
            self._size -= 1

    def update(self, dic: Dict[str, Any]):
        for k, v in dic.items():
            self[k] = v
        return self

    # 在HanLp的设计中，参数text是一个str，还是一个str的列表并不重要，在Trie的设计中会自动进行转换为字节序列
    # 全匹配算法
    def parse(self, text: Sequence[str]) -> List[Tuple[int, int, Any]]:
        """Keywords lookup which takes a piece of text as input, and lookup all occurrences of keywords in it. These
        occurrences can overlap with each other.

        Args:
            text: A piece of text. In HanLP's design, it doesn't really matter whether this is a str or a list of str.
                The trie will transit on either types properly, which means a list of str simply defines a list of
                transition criteria while a str defines each criterion as a character.

        Returns:
            A tuple of ``(begin, end, value)``.
        """
        found = []
        # 两层循环是为了控制词的开始和结束的索引
        for i in range(len(text)):
            # 第一层控制词的开头索引
            state = self  # 初始化状态：根节点
            for j in range(i, len(text)):
                # 第二层控制词的结尾索引
                state = state.transit(text[j])  # 判断当前字符在子节点字典中是否存在，并且赋值给当前状态字段（状态预改变）
                if state:  # 1、如果存在
                    if state._value is not None:  # 1.1、并且当前状态节点的_value值不为 None
                        found.append((i, j + 1, state._value))  # 1.1.1、添加进结果列表
                else:  # 2、如果不存在
                    break  # 2.1、跳出本层循环，说明当前字符在子节点字典中不存在，状态转移一定会失败
        return found

    # 最长匹配算法
    def parse_longest(self, text: Sequence[str]) -> List[Tuple[int, int, Any]]:
        """Longest-prefix-matching which tries to match the longest keyword sequentially from the head of the text till
        its tail. By definition, the matches won't overlap with each other.

        Args:
            text: A piece of text. In HanLP's design, it doesn't really matter whether this is a str or a list of str.
                The trie will transit on either types properly, which means a list of str simply defines a list of
                transition criteria while a str defines each criterion as a character.

        Returns:
            A tuple of ``(begin, end, value)``.

        """
        found = []
        i = 0
        while i < len(text):
            state = self.transit(text[i])
            if state:
                to = i + 1
                end = to
                value = state._value
                for to in range(i + 1, len(text)):
                    state = state.transit(text[to])
                    if not state:
                        break
                    if state._value is not None:
                        value = state._value
                        end = to + 1
                if value is not None:
                    found.append((i, end, value))
                    i = end - 1
            i += 1
        return found

    def items(self, ordered=False):
        yield from self._walk('', ordered)

    def __len__(self):
        return self._size

    def __bool__(self):
        return bool(len(self))
