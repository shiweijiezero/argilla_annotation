import argilla as rg
from argilla import User
from argilla.server.enums import UserRole
from datasets import Dataset, load_dataset
import pandas as pd
import random
from collections import defaultdict
import plotly.express as px


rg.init(
    api_url="http://127.0.0.1:6900",
    api_key="owner.apikey",
    workspace="admin"
)
workspace = rg.Workspace.create("test_workspace")
rg.set_workspace("test_workspace")

# 创建用户
user = rg.User.create(
    username="user1",
    first_name="New",
    last_name="User",
    password="shiweijie123",
    role=UserRole.annotator,
    workspaces=["test_workspace"]
)

user2 = rg.User.create(
    username="user2",
    first_name="New",
    last_name="User",
    password="shiweijie123",
    role=UserRole.annotator,
    workspaces=["test_workspace"]
)

data = load_dataset("argilla/databricks-dolly-15k-curated-multilingual", split="en")
df = data.to_pandas()
print(df)

# format the data as Argilla records
records = [rg.FeedbackRecord(fields={"category": record["category"], "instruction": record["instruction"], "response": record["response"], "context": record["context"]}, external_id=record['id']) for record in data]

# list of fields that we will use later for our dataset settings
fields = [
    rg.TextField(name="category", title="Task category"),
    rg.TextField(name="instruction"),
    rg.TextField(name="context", title="Input", required=False),
    rg.TextField(name="response")
]

# list of questions to display in the feedback form
questions =[
    rg.TextQuestion(
        name="new-instruction",
        title="Final instruction:",
        description="Write the final version of the instruction, making sure that it matches the task category. If the original instruction is ok, copy and paste it here.",
        required=True
    ),
    rg.TextQuestion(
        name="new-input",
        title="Final input:",
        description="Write the final version of the input, making sure that it makes sense with the task category. If the original input is ok, copy and paste it here. If an input is not needed, leave this empty.",
        required=False
    ),
    rg.TextQuestion(
        name="new-response",
        title="Final response:",
        description="Write the final version of the response, making sure that it matches the task category and makes sense for the instruction (and input) provided. If the original response is ok, copy and paste it here.",
        required=True
    )
]

guidelines = "In this dataset, you will find a collection of records that show a category, an instruction, an input and a response to that instruction. The aim of the project is to correct the instructions, input and responses to make sure they are of the highest quality and that they match the task category that they belong to. All three texts should be clear and include real information. In addition, the response should be as complete but concise as possible.\n\nTo curate the dataset, you will need to provide an answer to the following text fields:\n\n1 - Final instruction:\nThe final version of the instruction field. You may copy it using the copy icon in the instruction field. Leave it as it is if it's ok or apply any necessary corrections. Remember to change the instruction if it doesn't represent well the task category of the record.\n\n2 - Final input:\nThe final version of the instruction field. You may copy it using the copy icon in the input field. Leave it as it is if it's ok or apply any necessary corrections. If the task category and instruction don't need of an input to be completed, leave this question blank.\n\n3 - Final response:\nThe final version of the response field. You may copy it using the copy icon in the response field. Leave it as it is if it's ok or apply any necessary corrections. Check that the response makes sense given all the fields above.\n\nYou will need to provide at least an instruction and a response for all records. If you are not sure about a record and you prefer not to provide a response, click Discard."

users = [user for user in rg.User.list() if user.role =='annotator']

# shuffle the records to get a random assignment
random.shuffle(records)

# build a dictionary where the key is the username and the value is the list of records assigned to them
assignments = defaultdict(list)

# divide your records in chunks of the same length as the users list and make the assignments
# you will need to follow the instructions to create and push a dataset for each of the key-value pairs in this dictionary
n = len(users)
chunked_records = [records[i:i + n] for i in range(0, len(records), n)]
for chunk in chunked_records:
    for idx, record in enumerate(chunk):
        assignments[users[idx].username].append(record)

for username,records in assignments.items():
    # check that the user has a personal workspace and create it if not
    try:
        workspace = rg.Workspace.from_name(username)
    except:
        workspace = rg.Workspace.create(username)
        user = rg.User.from_name(username)
        workspace.add_user(user.id)

    # create a dataset for each annotator and push it to their personal workspace
    dataset = rg.FeedbackDataset(
        guidelines=guidelines,
        fields=fields,
        questions=questions
    )
    dataset.add_records(records)
    dataset.push_to_argilla(name='curate_dolly', workspace=workspace.name)


# feedback = []
# for username in assignments.keys():
#     feedback.extend(rg.FeedbackDataset.from_argilla('curate_dolly', workspace=username))
#
# responses = []
#
# for record in feedback:
#     if record.responses is None or len(record.responses) == 0:
#         continue
#
#     # we should only have 1 response per record, so we can safely use the first one only
#     response = record.responses[0]
#
#     if response.status != 'submitted':
#         changes = []
#     else:
#         changes = []
#         if response.values['new-instruction'].value != record.fields['instruction']:
#             changes.append('instruction')
#         if response.values['new-input'].value != record.fields['context']:
#             changes.append('input')
#         if response.values['new-response'].value != record.fields['response']:
#             changes.append('response')
#
#     responses.append({'status': response.status, 'category': record.fields['category'], 'changes': ','.join(changes)})
#
# responses_df = pd.DataFrame(responses)
# responses_df = responses_df.replace('', 'None')
#
# fig = px.histogram(responses_df, x='status')
# fig.show()
#
# fig = px.histogram(responses_df.loc[responses_df['status']=='submitted'], x='changes')
# fig.update_xaxes(categoryorder='total descending')
# fig.update_layout(bargap=0.2)
# fig.show()
#
# new_records = []
# for record in feedback:
#     if record.responses:
#         continue
#     # we should only have 1 response per record, so we can safely use the first one only
#     response = record.responses[0]
#     # we will skip records where our annotators didn't submit their feedback
#     if response.status != 'submitted':
#         continue
#
#     record.fields['instruction'] = response.values['new-instruction'].value
#     record.fields['context'] = response.values['new-input'].value
#     record.fields['response'] = response.values['new-response'].value
#
#     new_records.append(record.fields)
#
# new_df = pd.DataFrame(new_records)
# print(new_df)