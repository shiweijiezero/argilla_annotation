import json

import argilla as rg
from argilla.server.enums import UserRole
from tqdm import tqdm

def init_(work_space):
    rg.init(
        api_url="http://127.0.0.1:9999",
        api_key="owner.apikey"
    )
    # create_workspace
    try:
        wp = rg.Workspace.create(work_space)
        print(f"成功创建workspace {work_space}")
    except Exception as e:
        print(f"跳过创建workspace {work_space}")
        # traceback.print_exc()

    print(rg.list_workspaces())
    rg.set_workspace(work_space)

def read_data(file_name):
    with open(file_name,"r",encoding="utf-8") as f:
        data = json.load(f,)

    records = []
    for line_dic in tqdm(data,total=len(data)):
        question = line_dic["question"]
        answer = line_dic["answer"]
        ans1 = answer["ans1"]
        ans2 = answer["ans2"]

        record = rg.FeedbackRecord(fields={"prompt": question, "response-1": ans1, "response-2": ans2})
        records.append(record)

    return records

def create_user(user_name,work_space):
    try:
        user = rg.User.from_name(f"{user_name}")
    except Exception:
        print(f"创建用户{user_name}")
        user = rg.User.create(
            username=f"{user_name}",
            password=f"hkust{user_name}",
            role=UserRole.annotator,
            workspaces=[work_space]
        )
    #
    # user = rg.User.create(
    #     username="user1",
    #     first_name="New",
    #     last_name="User",
    #     password="shiweijie123",
    #     role=UserRole.annotator,
    #     workspaces=["test_workspace"]
    # )
    print(user)
    return user