import traceback

import argilla as rg

import utils

# init
project_name =  "HK_qa_demo"
work_space = "hkust"
utils.init_(work_space)

rg.delete(project_name,work_space)