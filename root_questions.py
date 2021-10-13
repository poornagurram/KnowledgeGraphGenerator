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

tuple_indices = {
    "id": 0,
    "node_name": 1,
    "synonyms": 2,
    "has_faq": 3,
    "node_type": -3,
    "display_name": -2,
    "auto_qualify": -1
}


def get_ques_info(question, root_node, parent_faq_map):
    for child in root_node.leaves:
        for i in range(len(parent_faq_map[child.name[0]][:])):
            if parent_faq_map[child.name[0]][i][0][1] == question:
                return child.name[1]


def parent_child_map(node):
    global map_child
    if node.is_leaf is True:
        return None
    else:
        # print(f"parent {node.name[1]}")
        map_child[(node.name[1], node.name[-2])] = []
        for i in node.children:
            # print(f"child {i.name[-1]}")
            map_child[(node.name[1], node.name[-2])].append((i.name[1], i.name[-2]))
            parent_child_map(i)


def create_root_nodes(intent_name=None, child_list=None, root_parent=None, question=None):
    current_children = []
    if intent_name is None:
        print("No intent name specified")
        return
    for child in child_list:
        if (root_parent.name[tuple_indices['node_name']], root_parent.name[tuple_indices['display_name']]) not in map_child:
            print(f"No concept called '{root_parent.name[tuple_indices['node_name']]}' available with display name {root_parent.name[tuple_indices['display_name']]}")
            print(f"******Heuristic exceptions*******")
            return
        for child_name, dis_name in map_child[(root_parent.name[tuple_indices['node_name']],
                                               root_parent.name[tuple_indices['display_name']])]:
            if child_name == child:
                current_children.append(child_name)
    new_children = set(child_list) - set(current_children)
    root_intent = findall(root_parent, filter_=lambda node: node.name[1] in (intent_name,))
    if root_intent is None or not root_intent:
        print(f"parent {root_parent} doesn't have intent {intent_name} defined")
        return
    else:
        root_intent = root_intent[0]
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
        temp_id = uuid.uuid4()
        parent_faq_map[root_child_intent.name[0]] = [[(temp_id, "~" + question)]]

    for child_name in current_children:
        current_child = findall(root_parent, filter_=lambda node: node.name[1] in (child_name,))[0]
        current_child_intent = findall(current_child, filter_=lambda node: node.name[1] in (intent_name,))
        if current_child_intent:
            current_child_intent = current_child_intent[0]
            current_child_intent.name = list(current_child_intent.name)
            current_child_intent.name[2].extend([str(intent_name) + " ooooo"])
            current_child_intent.name = tuple(current_child_intent.name)
        else:
            temp_id = uuid.uuid4()
            current_child_intent = Node((temp_id, intent_name, [str(intent_name) + " ooooo"], True, "default", ""),
                                     parent=current_child)
        temp_id = uuid.uuid4()
        root_child_intent = Node((temp_id, intent_name, [str(intent_name) + " ooooo"], True, "default", ""),
                                 parent=current_child)
        temp_id = uuid.uuid4()
        parent_faq_map[root_child_intent.name[0]] = [[(temp_id, "~" + question)]]


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
    root, parent_faq_map, parent_tags_map, parent_link_map = oa.fetch_ontology()
    print("before processing no of questions are", len(root.leaves))
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
    different_concept_name = []
    for row in root_df[['Parent', 'intent', 'Children', "Question"]].itertuples():
        parent_term = row.Parent
        intent_term = row.intent
        child_list = ast.literal_eval(row.Children)
        question = row.Question
        intent_id = findall(root, filter_=lambda node: node.name[1] in (parent_term,))
        if intent_id:
            if len(intent_id) > 1:
                print(f"multiple nodes found for {parent_term}")
                max_parent = intent_id[0]
                for i in range(len(intent_id)):
                    if len(max_parent.leaves) < len(intent_id[i].leaves):
                        max_parent = intent_id[i]
                create_root_nodes(intent_name=intent_term, child_list=child_list,
                                  root_parent=max_parent, question=question)
            else:
                create_root_nodes(intent_name=intent_term, child_list=child_list,
                                  root_parent=intent_id[0], question=question)
        else:
            print(f"Unable to find {parent_term}")
            different_concept_name.append(parent_term)
    print("after processing no of questions are", len(root.leaves))
    df_rows = []
    for i in root.leaves:
        row = []
        if i.name[0] not in parent_faq_map:
            continue
        # question id and question
        row.extend(list(parent_faq_map[i.name[0]][0][0]))
        temp = i
        path_list = []
        while temp:
            path = temp.name[tuple_indices['node_name']]+f"||{temp.name[tuple_indices['display_name']]}||"
            if temp.name[tuple_indices['auto_qualify']]:
                path = path+"true"
            if temp.name[tuple_indices['node_type']] == 'organizer':
                path = "!!"+path
            if "is" in temp.name[tuple_indices['synonyms']]:
                print("nodes", temp.name[tuple_indices['node_name']])
            if temp.name[tuple_indices['synonyms']]:
                syns = "/".join(temp.name[tuple_indices['synonyms']])
                syns = '('+syns+')'
                path = path+syns
            path_list.append(path)
            temp = temp.parent
        row.append(",".join(path_list[::-1]))
        try:
            row.extend(list(parent_link_map[i.name[0]][0]))
        except:
            row.extend(list((None, None)))
        # print(row)
        df_rows.append(row)
    df = pd.DataFrame(df_rows, columns=['Que ID', 'Primary Question', 'Path', 'faqLinkedBy', 'faqLinkedTo'])
    df[['Faq', 'Alternate Question', 'Tags', 'ReferenceId', 'Display Name', "isSoftDeleted",
        "Extended Answer-1", "Extended Answer-2"]] = ""
    df['Answer'] = df['Primary Question']
    df = df[["Faq", "Que ID", "Path", "Primary Question", "Alternate Question", "Tags", "Answer", "ReferenceId",
           "Display Name", "faqLinkedTo", "faqLinkedBy", "isSoftDeleted", "Extended Answer-1", "Extended Answer-2"]]

    df.to_csv("root_kg.csv", index=False)
    # print("\n".join(set(different_concept_name)))