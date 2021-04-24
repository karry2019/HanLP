/*
 * <summary></summary>
 * <author>He Han</author>
 * <email>hankcs.cn@gmail.com</email>
 * <create-date>2014/5/3 12:27</create-date>
 *
 * <copyright file="Node.java" company="上海林原信息科技有限公司">
 * Copyright (c) 2003-2014, 上海林原信息科技有限公司. All Right Reserved, http://www.linrunsoft.com/
 * This source is subject to the LinrunSpace License. Please contact 上海林原信息科技有限公司 to get more information.
 * </copyright>
 */
package com.hankcs.hanlp.collection.trie.bintrie;


import com.hankcs.hanlp.collection.trie.bintrie.util.ArrayTool;

/**
 * 深度大于等于2的子节点
 *
 * @author He Han
 */
public class Node<V> extends BaseNode {
    @Override
    protected boolean addChild(BaseNode node) {
        boolean add = false;
        if (child == null) {
            child = new BaseNode[0];
        }
        int index = ArrayTool.binarySearch(child, node);  // 在当前节点对象的子节点数组中进行查找
        if (index >= 0) { // 找到了需要添加的子节点
            BaseNode target = child[index];
            switch (node.status) {
                case UNDEFINED_0:  // 需要添加的节点状态为删除，既是想删除当前节点，就是把当前节点的状态置于target.status = Status.NOT_WORD_1，value=null
                    if (target.status != Status.NOT_WORD_1) {
                        target.status = Status.NOT_WORD_1;
                        target.value = null;
                        add = true;
                    }
                    break;
                case NOT_WORD_1:    // 添加节点，但不是词尾
                    if (target.status == Status.WORD_END_3) { // 原先是一个词的结尾并且不可以继续，变更为仍然是一个词的结尾，但是可以继续，因为添加的节点状态是路过，故在保留原来的词尾条件下，把不能继续变为可以继续
                        target.status = Status.WORD_MIDDLE_2;
                    }
                    break;
                case WORD_END_3:    // 添加节点：是单词的词尾
                    if (target.status != Status.WORD_END_3) { // 如果目标的状态不是(词尾并且不可继续)的状态，但添加的子节点肯定是一个词尾（是否可继续可忽略）
                        target.status = Status.WORD_MIDDLE_2;
                    }
                    if (target.getValue() == null) {  // 说明当前节点/词条在此之前已被删除，状态为UNDEFINED_0，本次添加操作必然改变状态标识，故状态标识add=true
                        add = true;
                    }
                    target.setValue(node.getValue());
                    break;
            }
        } else {    // 没找到
            BaseNode newChild[] = new BaseNode[child.length + 1];
            int insert = -(index + 1);  // index本身为负值，负值加一，相当于绝对值减一
            System.arraycopy(child, 0, newChild, 0, insert);
            System.arraycopy(child, insert, newChild, insert + 1, child.length - insert);
            newChild[insert] = node;
            child = newChild;
            add = true;
        }
        return add;
    }

    /**
     * @param c      节点的字符
     * @param status 节点状态
     * @param value  值
     */
    public Node(char c, Status status, V value) {
        this.c = c;
        this.status = status;
        this.value = value;
    }

    public Node() {
    }

    @Override
    public BaseNode getChild(char c) {
        if (child == null) return null;
        int index = ArrayTool.binarySearch(child, c);
        if (index < 0) return null;

        return child[index];
    }
}
