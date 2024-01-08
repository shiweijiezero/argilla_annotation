import traceback

import argilla as rg

import utils

# init
work_space = "hkust"
utils.init_(work_space)


# create_user
user1 = utils.create_user("user1", work_space)

print(rg.list_datasets(work_space))
print(rg.User.list())

# define a RankingQuestion
questions = [
    rg.RankingQuestion(
        name="response_ranking",
        title="Order the responses based on their accuracy and helpfulness:",
        required=True,
        values={"response-1": "Response 1", "response-2": "Response 2"}  # or ["response-1", "response-2"]
    )
]

# text field
fields = [
    rg.TextField(name="prompt", required=True),
    rg.TextField(name="response-1", required=True),
    rg.TextField(name="response-2", required=True)
]

# guidelines
dataset = rg.FeedbackDataset(
    guidelines="Please, read the prompt carefully and...",
    questions=questions,
    fields=fields
)

records = utils.read_data("./data/HK_qa_demo.json")
# Add records to the dataset
dataset.add_records(records)

# This publishes the dataset with its records to Argilla and returns the dataset in Argilla
remote_dataset = dataset.push_to_argilla(name="HK_qa_demo", workspace=work_space)
