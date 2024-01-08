import json
import os

import argilla as rg
from tqdm import tqdm

import utils

# # Assume we distribute the workload in one dataset across multiple labelers
# feedback = rg.FeedbackDataset.from_argilla(
#     name="my-dataset",
#     workspace="my-workspace"
# )

utils.init_("hkust")

# Assume the workload has been divided across the following workspaces
user_workspaces = ["hkust"]
project_name = "HK_qa_demo"
# This will hold each user's subsets
feedback_datasets = []

for workspace in user_workspaces:
    feedback = rg.FeedbackDataset.from_argilla(
        name=project_name,
        workspace=workspace
    )
    feedback_datasets.append(feedback)

print("响应为")
submit_count = 0
response_1_better_lst = []
response_2_better_lst = []
equal_1_lst = []
equal_2_lst = []
for feedback in feedback_datasets:
    records = list(feedback.records)
    for record in tqdm(records, total=len(records)):
        responses = record.responses
        if (responses):
            responses = responses[0]
            if (responses.status == "submitted"):
                submit_count += 1
                value = responses.values["response_ranking"].value
                field = record.fields
                value_dic = {}
                # [RankingValueSchema(value='response-1', rank=1), RankingValueSchema(value='response-2', rank=2)]
                for item in value:
                    name = item.value
                    rank = item.rank
                    value_dic[name] = rank
                if (value_dic['response-1'] < value_dic['response-2']):
                    response_1_better_lst.append(field)
                elif (value_dic['response-1'] > value_dic['response-2']):
                    response_2_better_lst.append(field)
                elif (value_dic['response-1'] == 1 and value_dic['response-2'] == 1):
                    equal_1_lst.append(field)
                elif (value_dic['response-1'] == 2 and value_dic['response-2'] == 2):
                    equal_2_lst.append(field)
print(f"submit_count:{submit_count}")
print(f"response_1_better_lst:{len(response_1_better_lst)}")
print(f"response_2_better_lst:{len(response_2_better_lst)}")
print(f"equal_1_lst:{len(equal_1_lst)}")
print(f"equal_2_lst:{len(equal_2_lst)}")

try:
    os.mkdir(f"./save_data/{project_name}")
except:
    pass


file_lst = [
    "response_1_better_lst","response_2_better_lst",
    "equal_1_lst","equal_2_lst",
]
obj_lst = [
    response_1_better_lst,response_2_better_lst,
    equal_1_lst,equal_2_lst,
]
for i in range(len(file_lst)):
    with open(f"./save_data/{project_name}/{file_lst[i]}.json","w") as f:
        json.dump(obj_lst[i],f)
