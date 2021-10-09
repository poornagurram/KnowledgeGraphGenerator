import argparse
import ast
import csv
import uuid
from anytree import Node
import pandas as pd
from analyzer.ontology_analyzer import OntologyAnalyzer
from anytree import RenderTree
from anytree.search import findall, find

map_child = dict()


def get_ques_info(question, root_node, parent_faq_map):
    for child in root_node.leaves:
        for i in range(len(parent_faq_map[child.name[0]][:])):
            if parent_faq_map[child.name[0]][i][0] == question:
                return child.name[1]


def parent_child_map(node):
    global map_child
    if node.is_leaf is True:
        return None
    else:
        # print(f"parent {node.name[1]}")
        map_child[(node.name[1], node.name[-1])] = []
        for i in node.children:
            # print(f"child {i.name[-1]}")
            map_child[(node.name[1], node.name[-1])].append((i.name[1], i.name[-1]))
            parent_child_map(i)


def create_root_nodes(intent_name=None, child_list=None, root_parent=None, question=None):
    current_children = []

    for child in child_list:
        for child_name, dis_name in map_child[(root_parent.name[1], root_parent.name[-1])]:
            if child_name == child:
                current_children.append(child_name)
    new_children = set(child_list) - set(current_children)
    root_intent = findall(root_parent, filter_=lambda node: node.name[1] in (intent_name,))[0]
    root_intent.name = list(root_intent.name)
    if root_intent.name[2] is None:
        root_intent.name[2] = [str(intent_name) + " xxxxx"]
    else:
        root_intent.name[2].extend([str(intent_name) + " xxxxx"])
    root_intent.name = tuple(root_intent.name)

    for child_name in new_children:
        temp_id = uuid.uuid4()
        root_child = Node((temp_id, child_name, [], True, "default", ""), parent=root_parent)
        temp_id = uuid.uuid4()
        root_child_intent = Node((temp_id, intent_name, [str(intent_name) + " ooooo"], True, "default", ""), parent=root_child)
        parent_faq_map[root_child_intent.name[0]] = "~" + question

    for child_name in current_children:
        current_child = findall(root_parent, filter_=lambda node: node.name[1] in (child_name,))[0]
        current_child_intent = findall(current_child, filter_=lambda node: node.name[1] in (intent_name,))[0]
        current_child_intent.name = list(current_child_intent.name)
        current_child_intent.name[2].extend([str(intent_name) + " ooooo"])
        current_child_intent.name = tuple(current_child_intent.name)
        temp_id = uuid.uuid4()
        root_child_intent = Node((temp_id, intent_name, [str(intent_name) + " ooooo"], True, "default", ""), parent=current_child)
        parent_faq_map[root_child_intent.name[0]] = "~" + question

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', help='path for input json file', required=True)
    parser.add_argument('--language', help='language of Ontology', default='en')
    _input_arguments = parser.parse_args()
    args = dict()
    args['input_file_path'] = _input_arguments.file_path
    args['language'] = _input_arguments.language
    oa = OntologyAnalyzer()
    oa.file_path = args['input_file_path']
    oa.read_file()
    root, parent_faq_map, parent_tags_map = oa.fetch_ontology()
    # intent_id = findall(root, filter_=lambda node: node.name[1] in ("Phase Three Merged",))
    question = "Why was a W-8 (NNW8) rejected?"
    # print(RenderTree(root))
    parent_child_map(root)
    # get_ques_info(question, root, parent_faq_map=parent_faq_map)
    # with open('accounts_children_pmpt_name.csv', 'w') as f:
    #     w = csv.writer(f)
    #     w.writerows(map_child.items())
    root_df = pd.read_csv("/home/poornaprudhvigurram/Downloads/root_questions_set1.csv")
    root_df['intent'] = root_df['Question'].apply(get_ques_info, root_node=root, parent_faq_map=parent_faq_map)
    for row in root_df[['Parent', 'intent', 'Children', "Question"]].itertuples():
        parent_term = row.Parent
        intent_term = row.intent
        child_list = ast.literal_eval(row.Children)
        question = row.Question
        intent_id = findall(root, filter_=lambda node: node.name[1] in (parent_term,))
        if len(intent_id) > 1:
            print("multiple nodes")
        else:
            create_root_nodes(intent_name=intent_term, child_list=child_list,
                              root_parent=intent_id[0], question=question)