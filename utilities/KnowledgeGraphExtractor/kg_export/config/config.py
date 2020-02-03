ontology_analyzer = {
    "LEAVES_WITHOUT_FAQS_LIMIT": 10,
    "CHAINS_OF_NODES_LIMIT": 10,
    "DUPLICATE_SIBLING_NODES_LIMIT": 50,
    "BETTER_MATCHED_PATHS_LIMIT": 50,
    "OVERLAPPING_ALTERNATE_QUESTIONS_LIMIT": 10,
    "QUESTIONS_WITH_MULTIPLE_MATCHED_PATHS_LIMIT": 50,
    "POSSIBLE_NEW_NODES_LIMIT": 50,
    "QUESTIONS_AT_ROOT_LIMIT": 10,
    "CHAINS_OF_NODES_MAX_LEVEL": 2,
    "NUMBER_OF_QUESTIONS_AT_ROOT_THRESHOLD": 50,
    "CYCLES_TO_SKIP_BEFORE_RUNNING_ONT_ANALYZER": 1,
    "NUMBER_OF_MULTIPLE_PATH_MATCHES": 2,
    "NODES_TO_RECOMMEND_IN_POSSIBLE_NEW_NODES": 2,
    "BETTER_MATCHED_PATHS_GIVEN_SCORE_LOWER_BOUND": 0.01,
    "BETTER_MATCHED_PATHS_MAX_SCORE_RATIO": 0.05,
    "PATH_COVERAGE": 50
}

log = {
    "FORMAT_STRING": "[%(asctime)s] p%(process)s %(levelname)s - %(message)s {%(pathname)s:%(lineno)d}",
    "SERVER_FORMAT_STRING": "[%(asctime)s] %(message)s",
    "ONTOLOGY_ANALYZER_LOG": "/home/lakshmikaivalya/Desktop/ontology analyzer/ont_analyzer.log",
    "DEBUG_LOG_LEVEL": "ERROR",
    "SERVER_LOG_LEVEL": "INFO"
}

""" All the delimiters used by json format """
TRAIT_DELIMITER = ':'
SYNONYM_DELIMITER = '/'

''' All the identifiers to recognize particular items in FAQ '''
NODE_IDENTIFIERS = ['**', '!!']
