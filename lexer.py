import json
import os
import re

path = os.path.dirname(__file__)
with open(os.path.join(path, "keywords.json"), "r", encoding="utf8") as f:
    semantic_keywords: dict[str, dict[str, str]] = json.load(f)

keywords: set[str] = set()
for keyword_type in semantic_keywords:
    keywords = keywords.union(set(semantic_keywords[keyword_type].keys()))


with open(os.path.join(path, "sample_program_1.txt")) as f:
    text = f.read()


def remove_comments(text: str) -> str:
    return re.sub(
        r"(/\*.+?\*/)", lambda match: " " * len(match.group(0)), text, flags=re.DOTALL
    )


def replace_tabs(text: str) -> str:
    return text.replace("\t", " " * 4)


def remove_extra_spaces_and_newlines(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def find_keyword(keyword_dict, word):
    stack = [keyword_dict]
    while stack:
        node = stack.pop()
        if word in node:
            return node, node[word]

        if isinstance(node, dict):
            for key, value in node.items():
                stack.append(value)


def find_string_literals(text: str) -> tuple[str, dict[str, str]]:
    string_literals = re.findall(r"(\".+?\")", text)
    string_literals_dict = {}
    for i, string in enumerate(string_literals):
        if not string:
            continue
        literal_name = f"__STR_LTRL_{i}"
        text = text.replace(string, literal_name)
        string_literals_dict[f"__STR_LTRL_{i}"] = string
    return text, string_literals_dict


def seperate_commas_colons_semicolons(text: str) -> str:
    return re.sub(r"\s*([,;])\s*|\s*(:=)\s*|\s*(:)\s*", r" \1\2\3 ", text)


def seperate_parenthesis_brackets(text: str) -> str:
    text = re.sub(r"\(\s*(.+?)\s*\)", r" ( \1 ) ", text)
    text = re.sub(r"\[\s*(.+?)\s*\]", r" [ \1 ] ", text)
    return text


def tokenize(phrase):
    tokens = []


processed_text = remove_comments(text)
processed_text = replace_tabs(processed_text)
processed_text = seperate_parenthesis_brackets(processed_text)
processed_text = remove_extra_spaces_and_newlines(processed_text)
processed_text, string_literals_dict = find_string_literals(processed_text)
processed_text,
processed_text = seperate_commas_colons_semicolons(processed_text)

print(processed_text)

tokens = []

statement = []
identifiers = {}
id_counter = 0

for phrase in processed_text.split():

    if phrase not in keywords:
        if not phrase.isdigit():
            id_name = f"__IDENT_" + str(id_counter)
            identifiers[id_name] = phrase
            statement.append(id_name)
            id_counter += 1
        else:
            statement.append(phrase)

    if phrase in keywords:
        if phrase in semantic_keywords["operators"]:
            statement.append(semantic_keywords["operators"][phrase])
        elif phrase in semantic_keywords["delimiters"]:
            statement.append(semantic_keywords["delimiters"][phrase])
            tokens.append("STATEMENT: " + " ".join(statement))
            statement.clear()
        else:
            if statement:
                tokens.append("STATEMENT: " + " ".join(statement))
                statement.clear()
            node, descriptor = find_keyword(semantic_keywords, phrase)
            tokens.append(descriptor)

# for id in identifiers.items():
#     print(id)
print(*tokens, sep="\n")

# print(identifiers)
